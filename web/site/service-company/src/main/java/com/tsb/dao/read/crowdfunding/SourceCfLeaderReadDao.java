package com.tsb.dao.read.crowdfunding;

import java.util.List;

import com.tsb.model.crowdfunding.SourceCfLeader;

public interface SourceCfLeaderReadDao {
	List<SourceCfLeader> getBySourceCfId(Integer sourceCfid);

	int count(Integer scfId);
}
