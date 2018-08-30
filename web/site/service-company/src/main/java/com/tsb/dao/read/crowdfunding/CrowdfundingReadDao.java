package com.tsb.dao.read.crowdfunding;

import java.util.List;

import org.apache.ibatis.annotations.Param;

import com.tsb.model.crowdfunding.Crowdfunding;
import com.tsb.model.crowdfunding.SourceCrowdfunding;
import com.tsb.model.vo.CfDBVO;
import com.tsb.model.vo.CfHeadVO;

public interface CrowdfundingReadDao {
	Crowdfunding getById(Integer cfId);

	List<SourceCrowdfunding> getByPage(int start);

	List<SourceCrowdfunding> getBySource(@Param("start") int start, @Param("source") int source);

	List<SourceCrowdfunding> getByStatus(@Param("start") int start, @Param("status") int status);

	List<SourceCrowdfunding> getByStatusAndSource(CfDBVO cf);

	int count();

	int countByStatus(int status);

	int countBySource(int source);

	int countByStatusAndSource(@Param("status") int status, @Param("source") int source);

}
