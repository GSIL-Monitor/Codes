package com.tsb.dao.read.crowdfunding;

import java.util.List;

import com.tsb.model.crowdfunding.SourceCfDocument;

public interface SourceCfDocumentReadDao {
	List<SourceCfDocument> getBySourceCfId(Integer sourceCfId);
}
