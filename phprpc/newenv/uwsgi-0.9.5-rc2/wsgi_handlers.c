#include "uwsgi.h"

extern struct uwsgi_server uwsgi;

PyObject *py_uwsgi_write(PyObject * self, PyObject * args) {
        PyObject *data;
        char *content;
        int len;

	struct wsgi_request *wsgi_req = current_wsgi_req(&uwsgi);

        data = PyTuple_GetItem(args, 0);
        if (PyString_Check(data)) {
                content = PyString_AsString(data);
                len = PyString_Size(data);

#ifdef UWSGI_THREADING
                if (uwsgi.has_threads && uwsgi.shared->options[UWSGI_OPTION_THREADS] == 1) {
                        Py_BEGIN_ALLOW_THREADS wsgi_req->response_size = write(wsgi_req->poll.fd, content, len);
                Py_END_ALLOW_THREADS}
                else {
#endif
                        wsgi_req->response_size = write(wsgi_req->poll.fd, content, len);
#ifdef UWSGI_THREADING
                }
#endif
        }

        Py_INCREF(Py_None);
        return Py_None;
}

#ifdef UWSGI_ASYNC

PyObject *py_eventfd_read(PyObject * self, PyObject * args) {
        int fd, timeout;

	struct wsgi_request *wsgi_req = current_wsgi_req(&uwsgi);

        if (!PyArg_ParseTuple(args, "i|i", &fd, &timeout)) {
                return NULL;
        }

        if (fd >= 0) {
                wsgi_req->async_waiting_fd = fd ;
                wsgi_req->async_waiting_fd_type = ASYNC_IN ;
                wsgi_req->async_waiting_fd_monitored = 0 ;
        }

        return PyString_FromString("") ;
}


PyObject *py_eventfd_write(PyObject * self, PyObject * args) {
        int fd, timeout;

	struct wsgi_request *wsgi_req = current_wsgi_req(&uwsgi);

        if (!PyArg_ParseTuple(args, "i|i", &fd, &timeout)) {
                return NULL;
        }

        if (fd >= 0) {
                wsgi_req->async_waiting_fd = fd ;
                wsgi_req->async_waiting_fd_type = ASYNC_OUT ;
                wsgi_req->async_waiting_fd_monitored = 0 ;
        }

        return PyString_FromString("") ;
}
#endif

int uwsgi_request_wsgi(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {

	int i;

	PyObject *zero, *wsgi_socket;

	PyObject *pydictkey, *pydictvalue;

	char *path_info;
	struct uwsgi_app *wi ;


#ifdef UWSGI_ASYNC
	if (wsgi_req->async_status == UWSGI_AGAIN) {
		// get rid of timeout
		if (wsgi_req->async_timeout_expired) {
			PyDict_SetItemString(wsgi_req->async_environ, "x-wsgiorg.fdevent.timeout", Py_True);
			wsgi_req->async_timeout_expired = 0 ;
		}
		else {
			PyDict_SetItemString(wsgi_req->async_environ, "x-wsgiorg.fdevent.timeout", Py_None);
		}
		return manage_python_response(uwsgi, wsgi_req);
	}
#endif

	/* Standard WSGI request */
	if (!wsgi_req->uh.pktsize) {
		fprintf(stderr, "Invalid WSGI request. skip.\n");
		return -1;
	}

	if (uwsgi_parse_vars(uwsgi, wsgi_req)) {
                fprintf(stderr,"Invalid WSGI request. skip.\n");
                return -1;
        }


#ifdef UWSGI_THREADING
	if (uwsgi->has_threads && !uwsgi->workers[uwsgi->mywid].i_have_gil) {
		PyEval_RestoreThread(uwsgi->_save);
		uwsgi->workers[uwsgi->mywid].i_have_gil = 1;
	}
#endif


	if (wsgi_req->script_name_len > 0) {
		zero = PyString_FromStringAndSize(wsgi_req->script_name, wsgi_req->script_name_len);
		if (PyDict_Contains(uwsgi->py_apps, zero)) {
                	wsgi_req->app_id = PyInt_AsLong(PyDict_GetItem(uwsgi->py_apps, zero));
                }
                else {
                	/* unavailable app for this SCRIPT_NAME */
                        wsgi_req->app_id = -1;
			if (wsgi_req->wsgi_script_len > 0 || (wsgi_req->wsgi_callable_len > 0 && wsgi_req->wsgi_module_len > 0)) {
				if ((wsgi_req->app_id = init_uwsgi_app(NULL, NULL)) == -1) {
					internal_server_error(wsgi_req->poll.fd, "wsgi application not found");
                			Py_DECREF(zero);
					goto clear2;
				}
			}
                }
                Py_DECREF(zero);
	} 


	if (wsgi_req->app_id == -1) {
		internal_server_error(wsgi_req->poll.fd, "wsgi application not found");
		goto clear2;

	}

	wi = &uwsgi->wsgi_apps[wsgi_req->app_id];

	if (uwsgi->single_interpreter == 0) {
		if (!wi->interpreter) {
			internal_server_error(wsgi_req->poll.fd, "wsgi application's %d interpreter not found");
			goto clear2;
		}

		// set the interpreter
		PyThreadState_Swap(wi->interpreter);
	}

	wi->requests++;


	if (wsgi_req->protocol_len < 5) {
		fprintf(stderr, "INVALID PROTOCOL: %.*s", wsgi_req->protocol_len, wsgi_req->protocol);
		internal_server_error(wsgi_req->poll.fd, "invalid HTTP protocol !!!");
		goto clear;

	}
	if (strncmp(wsgi_req->protocol, "HTTP/", 5)) {
		fprintf(stderr, "INVALID PROTOCOL: %.*s", wsgi_req->protocol_len, wsgi_req->protocol);
		internal_server_error(wsgi_req->poll.fd, "invalid HTTP protocol !!!");
		goto clear;
	}



#ifdef UWSGI_ASYNC
	wsgi_req->async_environ = wi->wsgi_environ[wsgi_req->async_id];
	wsgi_req->async_args = wi->wsgi_args[wsgi_req->async_id];
#else
	wsgi_req->async_environ = wi->wsgi_environ;
	wsgi_req->async_args = wi->wsgi_args;
#endif
	Py_INCREF((PyObject *)wsgi_req->async_environ);



	for (i = 0; i < wsgi_req->var_cnt; i += 2) {
		//fprintf(stderr,"%.*s: %.*s\n", wsgi_req->hvec[i].iov_len, wsgi_req->hvec[i].iov_base, wsgi_req->hvec[i+1].iov_len, wsgi_req->hvec[i+1].iov_base);
		pydictkey = PyString_FromStringAndSize(wsgi_req->hvec[i].iov_base, wsgi_req->hvec[i].iov_len);
		pydictvalue = PyString_FromStringAndSize(wsgi_req->hvec[i + 1].iov_base, wsgi_req->hvec[i + 1].iov_len);
		PyDict_SetItem(wsgi_req->async_environ, pydictkey, pydictvalue);
		Py_DECREF(pydictkey);
		Py_DECREF(pydictvalue);
	}


	if (wsgi_req->uh.modifier1 == UWSGI_MODIFIER_MANAGE_PATH_INFO) {
		pydictkey = PyDict_GetItemString(wsgi_req->async_environ, "SCRIPT_NAME");
		if (pydictkey) {
			if (PyString_Check(pydictkey)) {
				pydictvalue = PyDict_GetItemString(wsgi_req->async_environ, "PATH_INFO");
				if (pydictvalue) {
					if (PyString_Check(pydictvalue)) {
						path_info = PyString_AsString(pydictvalue);
						PyDict_SetItemString(wsgi_req->async_environ, "PATH_INFO", PyString_FromString(path_info + PyString_Size(pydictkey)));
					}
				}
			}
		}
	}




	// set wsgi vars

	wsgi_req->async_post = fdopen(wsgi_req->poll.fd, "r");

	wsgi_socket = PyFile_FromFile(wsgi_req->async_post, "wsgi_input", "r", NULL);
	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.input", wsgi_socket);
	Py_DECREF(wsgi_socket);

#ifdef UWSGI_SENDFILE
	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.file_wrapper", wi->wsgi_sendfile);
#endif

#ifdef UWSGI_ASYNC
	if (uwsgi->async > 1) {
		PyDict_SetItemString(wsgi_req->async_environ, "x-wsgiorg.fdevent.readable", wi->wsgi_eventfd_read);
		PyDict_SetItemString(wsgi_req->async_environ, "x-wsgiorg.fdevent.writable", wi->wsgi_eventfd_write);
		PyDict_SetItemString(wsgi_req->async_environ, "x-wsgiorg.fdevent.timeout", Py_None);
	}
#endif

	zero = PyTuple_New(2);
	PyTuple_SetItem(zero, 0, PyInt_FromLong(1));
	PyTuple_SetItem(zero, 1, PyInt_FromLong(0));
	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.version", zero);
	Py_DECREF(zero);

	zero = PyFile_FromFile(stderr, "wsgi_input", "w", NULL);
	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.errors", zero);
	Py_DECREF(zero);

	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.run_once", Py_False);

	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.multithread", Py_False);
	if (uwsgi->numproc == 1) {
		PyDict_SetItemString(wsgi_req->async_environ, "wsgi.multiprocess", Py_False);
	}
	else {
		PyDict_SetItemString(wsgi_req->async_environ, "wsgi.multiprocess", Py_True);
	}

	if (wsgi_req->scheme_len > 0) {
		zero = PyString_FromStringAndSize(wsgi_req->scheme, wsgi_req->scheme_len);
	}
	else if (wsgi_req->https_len > 0) {
		if (!strncasecmp(wsgi_req->https, "on", 2) || wsgi_req->https[0] == '1') {
			zero = PyString_FromString("https");
		}
		else {
			zero = PyString_FromString("http");
		}
	}
	else {
		zero = PyString_FromString("http");
	}
	PyDict_SetItemString(wsgi_req->async_environ, "wsgi.url_scheme", zero);
	Py_DECREF(zero);

	// call
#ifdef UWSGI_PROFILER
	if (uwsgi->enable_profiler == 1) {
		PyDict_SetItem(wi->pymain_dict, PyString_FromFormat("uwsgi_environ__%d", wsgi_req->app_id), wsgi_req->async_environ);
		wsgi_req->async_result = python_call(wi->wsgi_cprofile_run, wsgi_req->async_args);
		if (wsgi_req->async_result) {
			wsgi_req->async_result = PyDict_GetItemString(wi->pymain_dict, "uwsgi_out");
			Py_INCREF((PyObject*)wsgi_req->async_result);
			Py_INCREF((PyObject*)wsgi_req->async_result);
		}
	}
	else {
#endif


		PyTuple_SetItem(wsgi_req->async_args, 0, wsgi_req->async_environ);
		wsgi_req->async_result = python_call(wi->wsgi_callable, wsgi_req->async_args);

#ifdef UWSGI_PROFILER
	}
#endif


	if (wsgi_req->async_result) {


		while ( manage_python_response(uwsgi, wsgi_req) != UWSGI_OK) {
#ifdef UWSGI_ASYNC
			if (uwsgi->async > 1) {
				return UWSGI_AGAIN;
			}
#endif
		}


	}

clear:

	if (uwsgi->single_interpreter == 0) {
		// restoring main interpreter
		PyThreadState_Swap(uwsgi->main_thread);
	}

clear2:


	return UWSGI_OK;

}

void uwsgi_after_request_wsgi(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {

	if (uwsgi->shared->options[UWSGI_OPTION_LOGGING])
		log_request(wsgi_req);
}
