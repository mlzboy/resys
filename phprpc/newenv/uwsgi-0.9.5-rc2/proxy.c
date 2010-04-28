#ifdef UWSGI_PROXY

/* 

	uWSGI proxy

	it needs one of this tecnology to work:

	- epoll (linux 2.6)
	- kqueue (various BSD and Darwin)
	- /dev/poll (Solaris)

*/

#include "uwsgi.h"

#define UWSGI_PROXY_CONNECTING	1
#define UWSGI_PROXY_WAITING	2

extern struct uwsgi_server uwsgi;

struct uwsgi_proxy_connection {

	int dest_fd;
	int status;
	int retry;
	int node;
};

static void end_proxy(void) {
	exit(UWSGI_END_CODE);
}


static void reload_proxy(void) {
	exit(UWSGI_RELOAD_CODE);
}

static void uwsgi_proxy_close(struct uwsgi_proxy_connection *upcs, int fd) {


	if (upcs[fd].dest_fd >= 0) {
		close(upcs[fd].dest_fd);
		upcs[upcs[fd].dest_fd].dest_fd = -1;
		upcs[upcs[fd].dest_fd].status = 0;
		upcs[upcs[fd].dest_fd].retry = 0;
		if (upcs[upcs[fd].dest_fd].node > -1) {
			if (uwsgi.shared->nodes[upcs[upcs[fd].dest_fd].node].connections > 0)
				uwsgi.shared->nodes[upcs[upcs[fd].dest_fd].node].connections--;
		}
	}

	if (fd >= 0) {
		close(fd);
		upcs[fd].dest_fd = -1;
		upcs[fd].status = 0;
		upcs[fd].retry = 0;
		if (upcs[fd].node > -1) {
			if (uwsgi.shared->nodes[upcs[fd].node].connections > 0)
				uwsgi.shared->nodes[upcs[fd].node].connections--;
		}
	}

}

static int uwsgi_proxy_find_next_node(int current_node) {

	int i;

	current_node++;
	if (current_node >= MAX_CLUSTER_NODES) {
		current_node = 0;
	}

	// is it a good node ?
	if (uwsgi.shared->nodes[current_node].name[0] != 0 && uwsgi.shared->nodes[current_node].status == UWSGI_NODE_OK) {
		if (uwsgi.shared->nodes[current_node].connections < uwsgi.shared->nodes[current_node].workers)
			return current_node;
	}

	// try to find a better one

	for (i = 0; i < MAX_CLUSTER_NODES; i++) {
		if (uwsgi.shared->nodes[i].name[0] != 0 && uwsgi.shared->nodes[i].status == UWSGI_NODE_OK) {
			if (uwsgi.shared->nodes[i].connections < uwsgi.shared->nodes[i].workers)
				return i;
		}
	}

	// ok, it is a very loaded system, fallback to round robin
	if (uwsgi.shared->nodes[current_node].name[0] != 0 && uwsgi.shared->nodes[current_node].status == UWSGI_NODE_OK) {
		return current_node;
	}

	for (i = 0; i < MAX_CLUSTER_NODES; i++) {
		if (uwsgi.shared->nodes[i].name[0] != 0 && uwsgi.shared->nodes[i].status == UWSGI_NODE_OK) {
			return i;
		}
	}

	return -1;

}

void uwsgi_proxy(int proxyfd) {

	int efd ;

#ifdef __linux__
	struct epoll_event *eevents;
	struct epoll_event ev;
#elif defined(__sun__)
	struct pollfd *eevents;
	struct pollfd ev;
#else
	struct kevent *eevents;
	struct kevent ev;
#endif

	int max_events = 64;
	int nevents, i;
	const int nonblocking = 1;
	const int blocking = 0;

	char buffer[4096];
	ssize_t rlen;
	ssize_t wlen;
	int max_connections = sysconf(_SC_OPEN_MAX);

	int soopt;
	socklen_t solen = sizeof(int);

	int rc;

	struct uwsgi_proxy_connection *upcs;

	struct sockaddr_in upc_addr;
	socklen_t upc_len = sizeof(struct sockaddr_in);

	int next_node = -1;

	fprintf(stderr, "spawned uWSGI proxy (pid: %d)\n", getpid());

	fprintf(stderr, "allocating space for %d concurrent proxy connections\n", max_connections);

	// allocate memory for connections
	upcs = malloc(sizeof(struct uwsgi_proxy_connection) * max_connections);
	if (!upcs) {
		uwsgi_error("malloc()");
		exit(1);
	}
	memset(upcs, 0, sizeof(struct uwsgi_proxy_connection) * max_connections);


	efd = async_queue_init(proxyfd);
	if (efd < 0) {
		exit(1);
	}

#ifdef __linux__
	eevents = malloc(sizeof(struct epoll_event) * max_events);
	memset(&ev, 0, sizeof(struct epoll_event)); 
#elif defined(__sun)
	eevents = malloc(sizeof(struct pollfd) * max_events);
	memset(&ev, 0, sizeof(struct pollfd)); 
#else
	eevents = malloc(sizeof(struct kevent) * max_events);
	memset(&ev, 0, sizeof(struct kevent)); 
#endif

	if (!eevents) {
		uwsgi_error("malloc()");
		exit(1);
	}

	signal(SIGINT, (void *) &end_proxy);
	signal(SIGTERM, (void *) &reload_proxy);
	signal(SIGHUP, (void *) &reload_proxy);
	// and welcome to the loop...

	for (;;) {

		nevents = async_wait(efd, eevents, max_events, -1, 0);
		if (nevents < 0) {
			uwsgi_error("epoll_wait()");
			continue;
		}

		for (i = 0; i < nevents; i++) {


			if (eevents[i].ASYNC_FD == proxyfd) {

				if (eevents[i].ASYNC_IS_IN) {
					// new connection, accept it
					ev.ASYNC_FD = accept(proxyfd, (struct sockaddr *) &upc_addr, &upc_len);
					if (ev.ASYNC_FD < 0) {
						uwsgi_error("accept()");
						continue;
					}
					upcs[ev.ASYNC_FD].node = -1;

					// now connect to the first worker available

					upcs[ev.ASYNC_FD].dest_fd = socket(AF_INET, SOCK_STREAM, 0);
					if (upcs[ev.ASYNC_FD].dest_fd < 0) {
						uwsgi_error("socket()");
						uwsgi_proxy_close(upcs, ev.ASYNC_FD);
						continue;
					}
					upcs[upcs[ev.ASYNC_FD].dest_fd].node = -1;

					// set nonblocking
					if (ioctl(upcs[ev.ASYNC_FD].dest_fd, FIONBIO, &nonblocking)) {
						uwsgi_error("ioctl()");
						uwsgi_proxy_close(upcs, ev.ASYNC_FD);
						continue;
					}

					upcs[ev.ASYNC_FD].status = 0;
					upcs[ev.ASYNC_FD].retry = 0;
					next_node = uwsgi_proxy_find_next_node(next_node);
					if (next_node == -1) {
						fprintf(stderr, "unable to find an available worker in the cluster !\n");
						uwsgi_proxy_close(upcs, ev.ASYNC_FD);
						continue;
					}
					upcs[upcs[ev.ASYNC_FD].dest_fd].node = next_node;
					rc = connect(upcs[ev.ASYNC_FD].dest_fd, (struct sockaddr *) &uwsgi.shared->nodes[next_node].ucn_addr, sizeof(struct sockaddr_in));
					uwsgi.shared->nodes[next_node].connections++;

					if (!rc) {
						// connected to worker, put it in the epoll_list

						if (async_add(efd, ev.ASYNC_FD, ASYNC_IN)) {
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}

						upcs[upcs[ev.ASYNC_FD].dest_fd].dest_fd = ev.ASYNC_FD;
						upcs[upcs[ev.ASYNC_FD].dest_fd].status = 0;
						upcs[upcs[ev.ASYNC_FD].dest_fd].retry = 0;

						ev.ASYNC_FD = upcs[ev.ASYNC_FD].dest_fd;

						if (async_add(efd, ev.ASYNC_FD, ASYNC_IN)) {
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}

						// re-set blocking
						if (ioctl(upcs[upcs[ev.ASYNC_FD].dest_fd].dest_fd, FIONBIO, &blocking)) {
							uwsgi_error("ioctl()");
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}

					}
					else if (errno == EINPROGRESS) {
						// the socket is waiting, set status to CONNECTING
						upcs[ev.ASYNC_FD].status = UWSGI_PROXY_WAITING;
						upcs[upcs[ev.ASYNC_FD].dest_fd].dest_fd = ev.ASYNC_FD;
						upcs[upcs[ev.ASYNC_FD].dest_fd].status = UWSGI_PROXY_CONNECTING;
						upcs[upcs[ev.ASYNC_FD].dest_fd].retry = 0;

						ev.ASYNC_FD = upcs[ev.ASYNC_FD].dest_fd;
						if (async_add(efd, ev.ASYNC_FD, ASYNC_OUT)) {
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}
					}
					else {
						// connection failed, retry with the next node ?
						uwsgi_error("connect()");
						// close only when all node are tried
						uwsgi_proxy_close(upcs, ev.ASYNC_FD);
						continue;
					}


				}
				else {
					fprintf(stderr, "!!! something horrible happened to the uWSGI proxy, reloading it !!!\n");
					exit(1);
				}
			}
			else {
				// this is for clients/workers
				if (eevents[i].ASYNC_IS_IN) {

					// is this a connected client/worker ?
					//fprintf(stderr,"ready %d\n", upcs[eevents[i].data.fd].status);

					if (!upcs[eevents[i].ASYNC_FD].status) {
						if (upcs[eevents[i].ASYNC_FD].dest_fd >= 0) {

							rlen = read(eevents[i].ASYNC_FD, buffer, 4096);
							if (rlen < 0) {
								uwsgi_error("read()");
								uwsgi_proxy_close(upcs, eevents[i].ASYNC_FD);
								continue;
							}
							else if (rlen == 0) {
								uwsgi_proxy_close(upcs, eevents[i].ASYNC_FD);
								continue;
							}
							else {
								wlen = write(upcs[eevents[i].ASYNC_FD].dest_fd, buffer, rlen);
								if (wlen != rlen) {
									uwsgi_error("write()");
									uwsgi_proxy_close(upcs, eevents[i].ASYNC_FD);
									continue;
								}
							}
						}
						else {
							uwsgi_proxy_close(upcs, eevents[i].ASYNC_FD);
							continue;
						}
					}
					else if (upcs[eevents[i].ASYNC_FD].status == UWSGI_PROXY_WAITING) {
						// disconnected node
						continue;
					}
					else {
						fprintf(stderr, "UNKNOWN STATUS %d\n", upcs[eevents[i].ASYNC_FD].status);
						continue;
					}
				}
				else if (eevents[i].ASYNC_IS_OUT) {
					if (upcs[eevents[i].ASYNC_FD].status == UWSGI_PROXY_CONNECTING) {


#ifdef UWSGI_PROXY_USE_KQUEUE
						if (getsockopt(eevents[i].ASYNC_FD, SOL_SOCKET, SO_ERROR, (void *) (&soopt), &solen) < 0) {
							uwsgi_error("getsockopt()");
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}
						/* is something bad ? */
						if (soopt) {
							fprintf(stderr, "connect() %s\n", strerror(soopt));
							// increase errors on node
							fprintf(stderr, "*** marking cluster node %d/%s as failed ***\n", upcs[eevents[i].ASYNC_FD].node, uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].name);
							uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].errors++;
							uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].status = UWSGI_NODE_FAILED;
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}

						// increase errors on node
#endif
						ev.ASYNC_FD = upcs[eevents[i].ASYNC_FD].dest_fd;
						upcs[ev.ASYNC_FD].status = 0;
						if (async_add(efd, ev.ASYNC_FD, ASYNC_IN)) {
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}

						ev.ASYNC_FD = upcs[ev.ASYNC_FD].dest_fd;
						upcs[ev.ASYNC_FD].status = 0;

						if (async_mod(efd, ev.ASYNC_FD, ASYNC_IN)) {
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}
						// re-set blocking
						if (ioctl(ev.ASYNC_FD, FIONBIO, &blocking)) {
							uwsgi_error("ioctl()");
							uwsgi_proxy_close(upcs, ev.ASYNC_FD);
							continue;
						}
					}
					else {
						fprintf(stderr, "strange event for %d\n", (int) eevents[i].ASYNC_FD);
					}
				}
				else {
					if (upcs[eevents[i].ASYNC_FD].status == UWSGI_PROXY_CONNECTING) {
						if (getsockopt(eevents[i].ASYNC_FD, SOL_SOCKET, SO_ERROR, (void *) (&soopt), &solen) < 0) {
							uwsgi_error("getsockopt()");
						}
						/* is something bad ? */
						if (soopt) {
							fprintf(stderr, "connect() %s\n", strerror(soopt));
						}

						// increase errors on node
						fprintf(stderr, "*** marking cluster node %d/%s as failed ***\n", upcs[eevents[i].ASYNC_FD].node, uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].name);
						uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].errors++;
						uwsgi.shared->nodes[upcs[eevents[i].ASYNC_FD].node].status = UWSGI_NODE_FAILED;
					}
					else {
						fprintf(stderr, "STRANGE EVENT !!! %d %d %d\n", (int) eevents[i].ASYNC_FD, (int) eevents[i].ASYNC_EV, upcs[eevents[i].ASYNC_FD].status);
					}
					uwsgi_proxy_close(upcs, eevents[i].ASYNC_FD);
					continue;
				}
			}
		}
	}
}

#else
#warning "*** PROXY support is disabled ***"
#endif
