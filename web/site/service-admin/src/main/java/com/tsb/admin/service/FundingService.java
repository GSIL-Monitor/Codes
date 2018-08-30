package com.tsb.admin.service;

import java.util.List;

import com.tsb.admin.vo.FundingInvestorVO;
import com.tsb.admin.vo.FundingVO;
import com.tsb.admin.vo.SourceFundingVO;
import com.tsb.model.Funding;
import com.tsb.model.FundingInvestorRel;
import com.tsb.model.source.SourceFunding;
import com.tsb.model.source.SourceFundingInvestorRel;

public interface FundingService {
	List<Funding> get(Integer companyId);
	List<FundingVO> getFundingVO(Integer companyId);
	FundingVO getFundingVOByFundingId(Integer fundingId);
	
	//source
	List<SourceFundingVO> getSourceVO(Integer companyId);
	List<SourceFunding> getSourceFunding(Integer fundingId);
	
	List<SourceFundingInvestorRel> getSourceInvestorRel(Integer firId);
	
	//write
	Integer add(Funding funding);
	void update(Funding funding);
	void delete(Funding funding);
	
	FundingInvestorVO addFIR(FundingInvestorRel fir);
	void updateFIR(FundingInvestorRel fir);
	void deleteFIR(FundingInvestorRel fir);
}
