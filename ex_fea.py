#! /bin/env python
# encoding=utf-8
# zouxianqi@domob.cn
#  1.取train和test特征
#     需要激活idfa列表
#     需要原始tag标签
#
#
#


import sys

def get_act_user(path):
	user_act = {}
	fin = open(path, 'r')
	for l in fin:
		l = l.strip()
		user_act[l] = ""
	return user_act

def fea_cut(fea):
	if '::' in fea:
		fea_tmp = fea
		f_list = fea_tmp.split('::')
		if len(f_list) < 2:
			return fea
		fea = '::'.join(f_list[:2])
	return fea

def get_fea(fea_file_path, fea_map_all, fea_cnt_all):
	fea_dict = {}
	fea_file = open(fea_file_path, 'r')
	for l in fea_file:
		l = l.strip().split('\t')
		if len(l) != 3: continue

		idfa, type, fea = l
		if type == '20900':  continue

		fea = fea_cut(fea)
		if not fea_map_all.has_key(fea):
			fea_map_all[fea] = fea_cnt_all
			fea_cnt_all = fea_cnt_all + 1

		fea_idx  = fea_map_all[fea]
		if fea_dict.has_key(idfa):
			fea_vec = fea_dict[idfa]
			if fea_idx in fea_vec:
				fea_dict[idfa][fea_idx] += 1
			else:
				fea_dict[idfa][fea_idx] = 1
		else:
			fea_dict[idfa] = {fea_idx : 1}
	fea_file.close()
	return fea_dict, fea_map_all, fea_cnt_all
				
def fea_regulation(fea_dict):
	for idfa, feas in fea_dict.items():
		for fea_idx, v in feas.items():
			fea_dict[idfa][fea_idx] = 1	
	return fea_dict

def print_fea(fea_dict, user_act):
	for idfa, feas in fea_dict.items():
		label = '1' if idfa in user_act else '0'
		fea_str = label
		feas_sort = sorted(feas.items(), key = lambda k:k[0], reverse=False)
		for item in feas_sort:
			#liblinear fea index starts from 1
			fea_str += " "+str(item[0]+1)+":"+str(item[1])
		print "%s\t%s" % (idfa, fea_str)
		
def dump_fea_map(fpath, fea_cnt_all, fea_map_all):
	with open(fpath, 'w') as fout:
		fout.write("%d\n" % fea_cnt_all)
		for fea_str,index in fea_map_all.items():
			fout.write("%s\t%d\n" % (fea_str, index))

def load_fea_map(fpath):
	with open(fpath, 'r') as fin:
		fea_cnt_all = int( fin.readline().strip() )		
		for l in fin:
			l = l.strip().split('\t')
			fea_str = l[0]
			index   = int(l[1])
			fea_map_all[fea_str] = index
	return fea_cnt_all, fea_map_all
					
if __name__ == "__main__":		
	fea_map_all = {}
	fea_cnt_all = 0  
	#### train process
	train_act_user_path = 'user_act'
	train_raw_tag_path = 'train_data'
	train_act_user = get_act_user(train_act_user_path)
	fea_dict,fea_map_all,fea_cnt_all = get_fea(train_raw_tag_path, fea_map_all, fea_cnt_all)
	fea_dict = fea_regulation( fea_dict )
	print_fea(fea_dict, train_act_user) # get train feature
	dump_fea_map('fea_map.train', fea_cnt_all, fea_map_all)
    #### test process
	test_act_user_path = './test_user/test_act'
	test_raw_tag_path = './test_user/user_tag'
	fea_cnt_all, fea_map_all = load_fea_map('fea_map.train')
	test_act_user = get_act_user(test_act_user_path)
	fea_dict,fea_map_all,fea_cnt_all = get_fea(test_raw_tag_path, fea_map_all, fea_cnt_all)
	fea_dict = fea_regulation( fea_dict )
	print_fea(fea_dict, test_act_user)
	dump_fea_map('fea_map.test', fea_cnt_all, fea_map_all)

