package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.DocumentService;
import com.tsb.dao.read.company.DocumentReadDao;
import com.tsb.dao.write.company.DocumentWriteDao;
import com.tsb.model.company.Document;

@Service
public class DocumentServiceImpl implements DocumentService{

	@Autowired
	private DocumentReadDao documentReadDao;
	
	@Autowired
	private DocumentWriteDao documentWriteDao;

	@Override
	public List<Document> getAll(Integer companyId) {
		return documentReadDao.listByCompanyId(companyId);
	}

	@Override
	public void add(List<Document> documents, Integer userId) {
		for(Document document: documents){
			Timestamp time = new Timestamp(System.currentTimeMillis());
			document.setActive('Y');
			document.setCreateUser(userId);
			document.setCreateTime(time);
			documentWriteDao.insert(document);
		}
	}

	@Override
	public void delete(List<Integer> ids, Integer userId) {
		for(Integer id: ids){
			Timestamp time = new Timestamp(System.currentTimeMillis());
			Document document = new Document();
			document.setId(id);
			document.setActive('N');
			document.setModifyTime(time);
			document.setModifyUser(userId);
			documentWriteDao.delete(document);
		}
	}

}
