package com.tsb.company.service.org;

import java.util.Map;
@SuppressWarnings("rawtypes")
public interface TaskService {
	Map countTODO(Integer userId ,Integer filter);
	Map getTaskList(Integer userId,Integer filter,Integer from ,Integer pageSize,String type);
	Map getPublishList(Integer userId,Integer filter,Integer from ,Integer pageSize);
	Map getSelfList(Integer userId,Integer filter,Integer from ,Integer pageSize);
}
