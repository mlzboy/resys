#include "uwsgi.h"

/* uwsgi PING|100 */
int uwsgi_request_ping(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {
	char len;

	fprintf(stderr, "PING\n");
	wsgi_req->uh.modifier2 = 1;
	wsgi_req->uh.pktsize = 0;

	len = strlen(uwsgi->shared->warning_message);
	if (len > 0) {
		// endianess check is not needed as the warning message can be max 80 chars
		wsgi_req->uh.pktsize = len;
	}
	if (write(wsgi_req->poll.fd, wsgi_req, 4) != 4) {
		uwsgi_error("write()");
	}

	if (len > 0) {
		if (write(wsgi_req->poll.fd, uwsgi->shared->warning_message, len)
		    != len) {
			uwsgi_error("write()");
		}
	}

	return 0;
}

/* uwsgi ADMIN|10 */
int uwsgi_request_admin(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {
	uint32_t opt_value = 0;
	int i;

	if (wsgi_req->uh.pktsize >= 4) {
		memcpy(&opt_value, &wsgi_req->buffer, 4);
		// TODO: check endianess
	}
	fprintf(stderr, "setting internal option %d to %d\n", wsgi_req->uh.modifier2, opt_value);
	uwsgi->shared->options[wsgi_req->uh.modifier2] = opt_value;
	wsgi_req->uh.modifier1 = 255;
	wsgi_req->uh.pktsize = 0;
	wsgi_req->uh.modifier2 = 1;
	i = write(wsgi_req->poll.fd, wsgi_req, 4);
	if (i != 4) {
		uwsgi_error("write()");
	}

	return UWSGI_OK;
}

/* uwsgi FASTFUNC|26 */
int uwsgi_request_fastfunc(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {

	PyObject *ffunc;

#ifdef UWSGI_ASYNC
        if (wsgi_req->async_status == UWSGI_AGAIN) {
                return manage_python_response(uwsgi, wsgi_req);
        }
#endif

	ffunc = PyList_GetItem(uwsgi->fastfuncslist, wsgi_req->uh.modifier2);
	if (ffunc) {
		fprintf(stderr, "managing fastfunc %d\n", wsgi_req->uh.modifier2);
		return uwsgi_python_call(uwsgi, wsgi_req, ffunc, NULL);
	}

	return UWSGI_OK;
}

/* uwsgi MARSHAL|33 */
int uwsgi_request_marshal(struct uwsgi_server *uwsgi, struct wsgi_request *wsgi_req) {
	PyObject *func_result;

	PyObject *umm = PyDict_GetItemString(uwsgi->embedded_dict,
					     "message_manager_marshal");
	if (umm) {
		PyObject *ummo = PyMarshal_ReadObjectFromString(wsgi_req->buffer,
								wsgi_req->uh.pktsize);
		if (ummo) {
			if (!PyTuple_SetItem(uwsgi->embedded_args, 0, ummo)) {
				if (!PyTuple_SetItem(uwsgi->embedded_args, 1, PyInt_FromLong(wsgi_req->uh.modifier2))) {
					func_result = PyEval_CallObject(umm, uwsgi->embedded_args);
					if (PyErr_Occurred()) {
						PyErr_Print();
					}
					if (func_result) {
						PyObject *marshalled = PyMarshal_WriteObjectToString(func_result, 1);
						if (!marshalled) {
							PyErr_Print();
						}
						else {
							if (PyString_Size(marshalled) <= 0xFFFF) {
								wsgi_req->uh.pktsize = (uint16_t)
									PyString_Size(marshalled);
								if (write(wsgi_req->poll.fd, wsgi_req, 4) == 4) {
									if (write(wsgi_req->poll.fd, PyString_AsString(marshalled), wsgi_req->uh.pktsize) != wsgi_req->uh.pktsize) {
										uwsgi_error("write()");
									}
								}
								else {
									uwsgi_error("write()");
								}
							}
							else {
								fprintf(stderr, "marshalled object is too big. skip\n");
							}
							Py_DECREF(marshalled);
						}
						Py_DECREF(func_result);
					}
				}
			}
			//Py_DECREF(ummo);
		}
	}
	PyErr_Clear();

	return 0;
}
