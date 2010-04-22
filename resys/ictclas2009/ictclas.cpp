#include <boost/python.hpp>
#include <boost/python/list.hpp>
#include <string>
#include "ICTCLAS30.h"

using namespace boost::python;

struct my_result{
  int start; 
  int length; 
  std::string sPOS;
  int	iPOS;
  int word_ID; 
  int word_type; 
  int weight;
};


bool ict_init(const char* pDirPath)
{
	return ICTCLAS_Init(pDirPath);
}

bool ict_exit()
{
	return ICTCLAS_Exit();
}

unsigned int import_dict(const char *sFilename)
{
	return ICTCLAS_ImportUserDict(sFilename);
}

const char * process_str(const char *sParag, int bTagged)
{
	return ICTCLAS_ParagraphProcess(sParag, bTagged);
}

my_result& copy_result_t(my_result& re, const result_t& t)
{
	re.start = t.start;
	re.length = t.length;
	re.sPOS = std::string(&t.sPOS[0]);
	re.iPOS = t.iPOS;
	re.word_ID = t.word_ID;
	re.word_type = t.word_type;
	re.weight = t.weight;
	return re;
}

list process_str_ret_list(const char *sParag)
{
	int pResultCount = 0;
	const result_t* re = ICTCLAS_ParagraphProcessA(sParag, &pResultCount);
	list result;
	for (int i=0; i<pResultCount; i++)
	{
		my_result my_re;
		my_re = copy_result_t(my_re, re[i]);
		result.append(my_re);
	}
	return result;
}

bool process_file(const char *sSrcFilename,const char *sRetFilename,int bTagged)
{
	return ICTCLAS_FileProcess(sSrcFilename, sRetFilename, bTagged);
}

unsigned int process_str_ret_word_count(const char* sString)
{
	return ICTCLAS_GetParagraphProcessAWordCount(sString);
}

bool add_user_word(const char* sNewWord)
{
	return ICTCLAS_AddUserWord(sNewWord);
}

bool save_user_dict()
{
	return ICTCLAS_SaveTheUsrDic();
}

bool del_user_word(const char* sWord)
{
	int result = ICTCLAS_DelUsrWord(sWord);
	if (result == -1)
	{
		return false;
	}
	return true;
}

unsigned long fingerprint()
{
	return ICTCLAS_FingerPrint();
}

bool set_pos_map(int nPOSmap)
{
	return ICTCLAS_SetPOSmap(nPOSmap);
}

list keyword(int nCount)
{
	result_t* result_key  = new result_t[nCount];
	int nCountKey;
	ICTCLAS_KeyWord(result_key, nCountKey);
	list result;
	for (int i=0; i<nCountKey; i++)
	{
		my_result re;
		re = copy_result_t(re, result_key[i]);
		result.append(re);
	}
	delete [] result_key;
	return result;
}

enum POSMAP{ ICT_SECOND = ICT_POS_MAP_SECOND, \
			ICT_FIRST = ICT_POS_MAP_FIRST, \
			PKU_SECOND = PKU_POS_MAP_SECOND, \
			PKU_FIRST = PKU_POS_MAP_FIRST};

BOOST_PYTHON_MODULE(ictclas)
{
	class_<my_result>("result_t")
		.def_readonly("start", &my_result::start)
		.def_readonly("length", &my_result::length)
		.def_readonly("ipos", &my_result::iPOS)
		.def_readonly("word_id", &my_result::word_ID)
		// add in version 2009
		.def_readonly("spos", &my_result::sPOS)
		.def_readonly("word_type", &my_result::word_type)
		.def_readonly("weight", &my_result::weight);

	def("ict_init", ict_init);
	def("ict_exit", ict_exit);
	def("import_dict", import_dict);
	def("process_str", process_str);
	def("process_str_ret_list", process_str_ret_list);
	def("process_file", process_file);

	//add in version 2009
	def("process_str_ret_word_count", process_str_ret_word_count);
	def("keyword", keyword);
	def("add_user_word", add_user_word);
	def("save_user_dict", save_user_dict);
	def("del_user_word", del_user_word);
	def("fingerprint", fingerprint);
	def("set_pos_map", set_pos_map);

	enum_<POSMAP>("POSMAP")
		.value("ICT_SECOND", ICT_SECOND) 
		.value("ICT_FIRST", ICT_FIRST) 
		.value("PKU_SECOND", PKU_SECOND)
		.value("PKU_FIRST", PKU_FIRST); 
}
