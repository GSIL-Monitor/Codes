package com.tsb.company.service;

import java.util.List;

import com.tsb.model.company.Document;

public interface DocumentService {
	List<Document> getAll(Integer companyId);
	void add(List<Document> documents, Integer userId);
	void delete(List<Integer> ids, Integer userId);
}
