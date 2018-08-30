package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.read.FundingInvestorRelReadDao;
import com.tsb.admin.dao.read.FundingReadDao;
import com.tsb.admin.dao.read.InvestorReadDao;
import com.tsb.admin.dao.read.source.SourceFundingInvestorRelReadDao;
import com.tsb.admin.dao.read.source.SourceFundingReadDao;
import com.tsb.admin.dao.read.source.SourceInvestorReadDao;
import com.tsb.admin.dao.write.FundingInvestorRelWriteDao;
import com.tsb.admin.dao.write.FundingWriteDao;
import com.tsb.admin.service.CompanyService;
import com.tsb.admin.service.FundingService;
import com.tsb.admin.vo.FundingInvestorVO;
import com.tsb.admin.vo.FundingVO;
import com.tsb.admin.vo.SourceFundingInvestorVO;
import com.tsb.admin.vo.SourceFundingVO;
import com.tsb.model.Funding;
import com.tsb.model.FundingInvestorRel;
import com.tsb.model.Investor;
import com.tsb.model.source.SourceFunding;
import com.tsb.model.source.SourceFundingInvestorRel;

@Service
public class FundingServiceImpl implements FundingService {

	@Autowired
	private FundingReadDao fundingReadDao;
	
	@Autowired
	private FundingInvestorRelReadDao firReadDao;
	
	@Autowired
	private InvestorReadDao investorReadDao;
	
	@Autowired
	private SourceFundingReadDao sfReadDao;
	
	@Autowired
	private SourceFundingInvestorRelReadDao sfirReadDao;
	
	@Autowired
	private SourceInvestorReadDao siReadDao;
	
	@Autowired
	private FundingWriteDao fundingWriteDao;
	
	@Autowired
	private FundingInvestorRelWriteDao firWriteDao;
	
	@Autowired
	private CompanyService companyService;
	

	@Override
	public List<Funding> get(Integer companyId) {
		return fundingReadDao.get(companyId);
	}
	
	
	@Override
	public List<FundingVO> getFundingVO(Integer companyId) {
		List<Funding> fundingList =fundingReadDao.get(companyId);
		List<FundingVO> fundingVOList = new ArrayList<FundingVO>();
		
		for (Funding funding: fundingList){
			FundingVO fVO = new FundingVO();
			fVO.setFunding(funding);
			List<FundingInvestorRel> firList =  firReadDao.get(funding.getId());
			List<FundingInvestorVO> fiVOList  = new ArrayList<FundingInvestorVO>();
			for (FundingInvestorRel fir: firList){
				FundingInvestorVO fiVO = new FundingInvestorVO();
				fiVO.setFundingInvestorRel(fir);
				fiVO.setInvestor(investorReadDao.getById(fir.getInvestorId()));
				fiVOList.add(fiVO);
			}
			
			fVO.setFundingInvestorList(fiVOList);
			fundingVOList.add(fVO);
		}
		
		return fundingVOList;
	}
	
	@Override
	public FundingVO getFundingVOByFundingId(Integer fundingId) {
		Funding funding =fundingReadDao.getByFundingId(fundingId);
		FundingVO fVO = new FundingVO();
		fVO.setFunding(funding);
		
		List<FundingInvestorRel> firList =  firReadDao.get(funding.getId());
		List<FundingInvestorVO> fiVOList  = new ArrayList<FundingInvestorVO>();
		for (FundingInvestorRel fir: firList){
			FundingInvestorVO fiVO = new FundingInvestorVO();
			fiVO.setFundingInvestorRel(fir);
			fiVO.setInvestor(investorReadDao.getById(fir.getInvestorId()));
			fiVOList.add(fiVO);
		}
		
		fVO.setFundingInvestorList(fiVOList);
		
		return fVO;
	}

	
	@Override
	public List<SourceFundingVO> getSourceVO(Integer fundingId) {
		List<SourceFunding> sfList =sfReadDao.getByFundingId(fundingId);
		List<SourceFundingVO> sfVOList = new ArrayList<SourceFundingVO>();
		for(SourceFunding sf: sfList){
			SourceFundingVO sfVO = new SourceFundingVO();
			sfVO.setSourceFunding(sf);
			
			List<SourceFundingInvestorRel> sfirList =  sfirReadDao.get(sf.getId());
			List<SourceFundingInvestorVO> sfiVOList  = new ArrayList<SourceFundingInvestorVO>();
			for (SourceFundingInvestorRel sfir: sfirList){
				SourceFundingInvestorVO sfiVO = new SourceFundingInvestorVO();
				sfiVO.setSfiRel(sfir);
				sfiVO.setSourceInvestor((siReadDao.getById(sfir.getSourceInvestorId())));
				sfiVOList.add(sfiVO);
			}
			
			sfVO.setSfiVOList(sfiVOList);
			sfVOList.add(sfVO);
		}
		
		return sfVOList;
		
	}
	
	@Override
	public List<SourceFunding> getSourceFunding(Integer fundingId) {
		return sfReadDao.getByFundingId(fundingId);
	}
	
	@Override
	public List<SourceFundingInvestorRel> getSourceInvestorRel(Integer firId) {
		return sfirReadDao.get(firId);
	}


	
	/************** write  **********/
	
	@Override
	public Integer add(Funding funding) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		
		funding.setCreateTime(time);
		funding.setVerify('Y');
		funding.setActive('Y');
		funding.setCreateUser(0);
		
		fundingWriteDao.insert(funding);
		
		// update company funding part
		
//		companyService.updateFunding(company);
		
		
		
		
		
		return funding.getId();
	}

	@Override
	public void update(Funding funding) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		funding.setModifyTime(time);
		funding.setVerify('Y');
		funding.setModifyUser(0);
		fundingWriteDao.update(funding);
	}


	@Override
	public void delete(Funding funding) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		funding.setModifyTime(time);
		funding.setActive('N');
		funding.setModifyUser(0);
		fundingWriteDao.update(funding);
	}


	@Override
	public FundingInvestorVO addFIR(FundingInvestorRel fir) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		fir.setCreateTime(time);
		fir.setVerify('Y');
		fir.setActive('Y');
		fir.setCreateUser(0);
		firWriteDao.insert(fir);
		
		Investor investor = investorReadDao.getById(fir.getInvestorId());
		
		FundingInvestorVO fiVO = new FundingInvestorVO();
		fiVO.setFundingInvestorRel(fir);
		fiVO.setInvestor(investor);
		
		return fiVO;
	}


	@Override
	public void updateFIR(FundingInvestorRel fir) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		fir.setModifyTime(time);
		fir.setVerify('Y');
		fir.setModifyUser(0);
		firWriteDao.update(fir);
		
	}


	@Override
	public void deleteFIR(FundingInvestorRel fir) {
		Timestamp time = new Timestamp(System.currentTimeMillis());	
		fir.setModifyTime(time);
		fir.setActive('N');
		fir.setModifyUser(0);
		
		firWriteDao.update(fir);
	}


}
