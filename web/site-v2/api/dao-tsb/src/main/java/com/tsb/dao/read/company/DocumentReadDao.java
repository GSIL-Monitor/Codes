package com.tsb.dao.read.company;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.company.Document;

public interface DocumentReadDao {

	Document getById(Integer id);

	List<Document> listByCompanyId(Integer companyId);

	List<Document> listByCompanyIdAndType(@Param("companyId") Integer companyId, @Param("type") Integer type);
}
