#ifdef UWSGI_SNMP

#include "uwsgi.h"

extern struct uwsgi_server uwsgi;

#define SNMP_SEQUENCE 0x30
#define SNMP_INTEGER 0x02
#define SNMP_STRING 0x04
#define SNMP_NULL 0x05
#define SNMP_GET 0xA0
#define SNMP_RES 0xA2
#define SNMP_OID 0x06

#define SNMP_WATERMARK (127-8)

/* 1.3.6.1.4.1.35156.17.X.X */
#define SNMP_UWSGI_BASE "\x2B\x06\x01\x04\x01\x82\x92\x54\x11"

static int get_snmp_integer(uint8_t *, uint64_t *);

static uint64_t get_uwsgi_snmp_value(uint64_t, uint8_t *);
static uint64_t get_uwsgi_custom_snmp_value(uint64_t, uint8_t *);

static uint8_t snmp_int_to_snmp(uint64_t, uint8_t, uint8_t *);

static ssize_t build_snmp_response(uint8_t, uint8_t, uint8_t *, int, uint8_t *, uint8_t *, uint8_t *);

void manage_snmp(int fd, uint8_t * buffer, int size, struct sockaddr_in *client_addr) {

	uint16_t asnlen;
	uint16_t oidlen;

	uint8_t oid_part[2];

	int ptrdelta;

	uint8_t *ptr = buffer, *seq1, *seq2, *seq3;

	uint8_t community_len;

	uint64_t snmp_int;
	uint64_t request_id;
	uint64_t version;

	// KISS for memory management
	if (size > SNMP_WATERMARK)
		return;
	ptr++;

	// check total sequence size
	if (*ptr > SNMP_WATERMARK || *ptr < 13)
		return;
	ptr++;


	// check snmp version   
	if (*ptr != SNMP_INTEGER)
		return;
	ptr++;

	ptrdelta = get_snmp_integer(ptr, &version);
	if (version > 2)
		return;
	ptr += ptrdelta;



	// check for community string (this must be set from the python vm using uwsgi.snmp_community or with --snmp-community arg)
	if (*ptr != SNMP_STRING)
		return;
	ptr++;

	community_len = *ptr;



	if (community_len > 72 || community_len < 1)
		return;
	ptr++;

	// check for community string
	if (strlen(uwsgi.shared->snmp_community) != community_len)
		return;
	if (memcmp(ptr, uwsgi.shared->snmp_community, community_len))
		return;

	ptr += community_len;

	// check for get request
	if (*ptr != SNMP_GET)
		return;
	*ptr = SNMP_RES;
	ptr++;
	seq1 = ptr;


	if (*ptr != ((size - community_len) - 9))
		return;
	ptr++;



	// get request_id
	if (*ptr != SNMP_INTEGER)
		return;
	ptr++;
	ptrdelta = get_snmp_integer(ptr, &request_id);


	if (ptrdelta <= 0)
		return;

	// check here
	if (ptr + ptrdelta >= buffer + size)
		return;
	ptr += ptrdelta;

	// get error
	if (*ptr != SNMP_INTEGER)
		return;
	ptr++;
	ptrdelta = get_snmp_integer(ptr, &snmp_int);
	if (ptrdelta <= 0)
		return;
	if (ptr + ptrdelta >= buffer + size)
		return;
	if (snmp_int != 0)
		return;
	ptr += ptrdelta;

	// get index
	if (*ptr != SNMP_INTEGER)
		return;
	ptr++;
	ptrdelta = get_snmp_integer(ptr, &snmp_int);
	if (ptrdelta <= 0)
		return;
	if (ptr + ptrdelta >= buffer + size)
		return;

	if (snmp_int != 0)
		return;
	ptr += ptrdelta;

	// check for sequence
	if (*ptr != SNMP_SEQUENCE)
		return;
	ptr++;


	if (*ptr > SNMP_WATERMARK)
		return;
	seq2 = ptr;
	ptr++;

	// now the interesting stuff: OID management
	if (*ptr != SNMP_SEQUENCE)
		return;
	ptr++;



	// check for normal OID uWSGI size: |1.3|.6|.1|.4|.1.|35156|.17|.1/2|.x| + OID_NULL
	asnlen = *ptr;
	if (asnlen < 15)
		return;
	seq3 = ptr;
	ptr++;

	// is it an OID ?
	if (*ptr != SNMP_OID)
		return;
	ptr++;


	oidlen = *ptr;
	if (oidlen != 11)
		return;
	ptr++;

	// and now parse the OID !!!
	if (memcmp(ptr, SNMP_UWSGI_BASE, 9))
		return;

	ptr += 9;

	oid_part[0] = *ptr;

	if (oid_part[0] != 1 && oid_part[0] != 2)
		return;
	ptr++;

	oid_part[1] = *ptr;
	if (oid_part[1] < 1 || oid_part[1] > 100)
		return;
	ptr++;

	// check for null
	if (memcmp((char *) ptr, "\x05\x00", 2))
		return;
	ptr += 2;


	size = build_snmp_response(oid_part[0], oid_part[1], buffer, size, seq1, seq2, seq3);

	if (size > 0) {
		if (sendto(fd, buffer, size, 0, (struct sockaddr *) client_addr, sizeof(struct sockaddr_in)) < 0) {
			uwsgi_error("sendto()");
		}
	}

}

static uint64_t get_uwsgi_snmp_value(uint64_t val, uint8_t * oid_t) {

	val--;

	if (uwsgi.shared->snmp_gvalue[val].type) {
		*oid_t = uwsgi.shared->snmp_gvalue[val].type;
		return *uwsgi.shared->snmp_gvalue[val].val;
	}

	*oid_t = SNMP_NULL;
	return 0;
}

static uint64_t get_uwsgi_custom_snmp_value(uint64_t val, uint8_t * oid_t) {

	val--;
	if (uwsgi.shared->snmp_value[val].type) {
		*oid_t = uwsgi.shared->snmp_value[val].type;
		return uwsgi.shared->snmp_value[val].val;
	}

	*oid_t = SNMP_NULL;
	return 0;

}

static int get_snmp_integer(uint8_t * ptr, uint64_t * val) {

	uint16_t tlen;
	int i, j;

	tlen = *ptr;

	if (tlen > 4)
		return -1;


	j = 0;
#ifdef __BIG_ENDIAN__
	for (i = 0; i < tlen; i++) {
#else
	for (i = tlen - 1; i >= 0; i--) {
#endif
		val[j] = ptr[1 + i];
		j++;
	}

	return tlen + 1;
}

static uint8_t snmp_int_to_snmp(uint64_t snmp_val, uint8_t oid_type, uint8_t * buffer) {

	uint8_t tlen;
	int i, j;
	uint8_t *ptr = (uint8_t *) & snmp_val;


	// check for counter, counter64 or gauge

	if (oid_type == SNMP_COUNTER64) {
		tlen = 8;
	}
	else if (oid_type == SNMP_NULL || oid_type == 0) {
		tlen = 0;
	}
	else {
		tlen = 4;
	}

	buffer[0] = tlen;

	j = 1;
#ifdef __BIG_ENDIAN__
	for (i = 0; i < tlen; i++) {
#else
	for (i = tlen - 1; i >= 0; i--) {
#endif
		buffer[j] = ptr[i];
		j++;
	}

	return tlen + 1;
}

static ssize_t build_snmp_response(uint8_t oid1, uint8_t oid2, uint8_t * buffer, int size, uint8_t * seq1, uint8_t * seq2, uint8_t * seq3) {

	uint64_t snmp_val;
	uint8_t oid_sz;
	uint8_t oid_type;

	if (oid1 == 1) {
		snmp_val = get_uwsgi_snmp_value(oid2, &oid_type);
	}
	else if (oid1 == 2) {
		snmp_val = get_uwsgi_custom_snmp_value(oid2, &oid_type);
	}
	else {
		return -1;
	}

	buffer[size - 2] = oid_type;
	oid_sz = snmp_int_to_snmp(snmp_val, oid_type, buffer + (size - 1));

	if (oid_sz < 1)
		return -1;

	oid_sz--;

	buffer[1] += oid_sz;
	*seq1 += oid_sz;
	*seq2 += oid_sz;
	*seq3 += oid_sz;

	return size + oid_sz;

}

PyObject *py_snmp_counter32(PyObject * self, PyObject * args) {

	uint8_t oid_num;
	uint32_t oid_val = 0;

	if (!PyArg_ParseTuple(args, "bi:snmp_set_counter32", &oid_num, &oid_val)) {
		return NULL;
	}

	if (oid_num > 100 || oid_num < 1)
		goto clear;

	uwsgi.shared->snmp_value[oid_num - 1].type = SNMP_COUNTER32;
	uwsgi.shared->snmp_value[oid_num - 1].val = oid_val;

	Py_INCREF(Py_True);
	return Py_True;

      clear:

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *py_snmp_counter64(PyObject * self, PyObject * args) {

	uint8_t oid_num;
	uint64_t oid_val = 0;

	if (!PyArg_ParseTuple(args, "bl:snmp_set_counter64", &oid_num, &oid_val)) {
		return NULL;
	}

	if (oid_num > 100 || oid_num < 1)
		goto clear;

	uwsgi.shared->snmp_value[oid_num - 1].type = SNMP_COUNTER64;
	uwsgi.shared->snmp_value[oid_num - 1].val = oid_val;

	Py_INCREF(Py_True);
	return Py_True;

      clear:

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *py_snmp_gauge(PyObject * self, PyObject * args) {

	uint8_t oid_num;
	uint32_t oid_val = 0;

	if (!PyArg_ParseTuple(args, "bi:snmp_set_gauge", &oid_num, &oid_val)) {
		return NULL;
	}

	if (oid_num > 100 || oid_num < 1)
		goto clear;

	uwsgi.shared->snmp_value[oid_num - 1].type = SNMP_GAUGE;
	uwsgi.shared->snmp_value[oid_num - 1].val = oid_val;

	Py_INCREF(Py_True);
	return Py_True;

      clear:

	Py_INCREF(Py_None);
	return Py_None;
}

PyObject *py_snmp_community(PyObject * self, PyObject * args) {

	char *snmp_community;

	if (!PyArg_ParseTuple(args, "s:snmp_set_community", &snmp_community)) {
		return NULL;
	}

	if (strlen(snmp_community) > 72) {
		fprintf(stderr, "*** warning the supplied SNMP community string will be truncated to 72 chars ***\n");
		memcpy(uwsgi.shared->snmp_community, snmp_community, 72);
	}
	else {
		strcpy(uwsgi.shared->snmp_community, snmp_community);
	}

	Py_INCREF(Py_True);
	return Py_True;

}

static PyMethodDef uwsgi_snmp_methods[] = {
	{"snmp_set_counter32", py_snmp_counter32, METH_VARARGS, ""},
	{"snmp_set_counter64", py_snmp_counter64, METH_VARARGS, ""},
	{"snmp_set_gauge", py_snmp_gauge, METH_VARARGS, ""},
	{"snmp_set_community", py_snmp_community, METH_VARARGS, ""},
	{NULL, NULL},
};

void snmp_init() {

	PyMethodDef *uwsgi_function;

	for (uwsgi_function = uwsgi_snmp_methods; uwsgi_function->ml_name != NULL; uwsgi_function++) {
		PyObject *func = PyCFunction_New(uwsgi_function, NULL);
		PyDict_SetItemString(uwsgi.embedded_dict, uwsgi_function->ml_name, func);
		Py_DECREF(func);
	}

	fprintf(stderr, "SNMP python functions initialized.\n");
}



#else
#warning "*** SNMP support is disabled ***"
#endif
