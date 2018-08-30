package com.tsb.company.service;

import java.util.List;

import com.tsb.company.vo.CompsVO;


@SuppressWarnings("rawtypes")
public interface CompaniesRelService {
	CompsVO getByCode(String code);
	List get(Integer companyId);
	void add(List<Integer> ids, Integer companyId, Integer userId);
	void delete(List<Integer> ids,Integer companyId,  Integer userId);
}
