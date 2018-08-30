package com.tsb.company.service;

import java.util.List;

import com.tsb.model.company.Tag;

public interface TagService {
	void addTagRels(Integer companyId, List<Integer> ids, Integer userId);
	void deleteTagRels(Integer companyId, List<Integer> ids, Integer userId);
	
	void addTagRel(Integer companyId, Tag tag, Integer userId);
	void deleteTagRel(Integer companyId, Integer tagId, Integer userId);
	
	List<Tag> getTags(Integer companyId);
	
	Tag addTag(String name,Integer userId);
	
	Tag getByName(String name);
}
