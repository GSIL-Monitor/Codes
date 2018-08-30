package com.tsb.dao.read.crowdfunding;

import com.tsb.model.crowdfunding.SourceCrowdfunding;
import com.tsb.model.vo.CfHeadVO;

public interface SourceCrowdfundingReadDao {
	SourceCrowdfunding getBycfId(Integer cfId);
	CfHeadVO getCfHeadInfo(Integer cfId);
}
