package com.tsb.dao.write.company;

import com.tsb.model.company.Document;

public interface DocumentWriteDao {
	void insert(Document document);
	void delete(Document document);
}
