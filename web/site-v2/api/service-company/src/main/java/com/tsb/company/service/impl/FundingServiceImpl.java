package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.FundingService;
import com.tsb.company.vo.FundingInvestorRelVO;
import com.tsb.company.vo.FundingVO;
import com.tsb.dao.read.company.FundingInvestorRelReadDao;
import com.tsb.dao.read.company.FundingReadDao;
import com.tsb.dao.read.company.InvestorReadDao;
import com.tsb.dao.write.company.FundingInvestorRelWriteDao;
import com.tsb.dao.write.company.FundingWriteDao;
import com.tsb.model.company.Funding;
import com.tsb.model.company.FundingInvestorRel;

@Service
@SuppressWarnings("rawtypes")
public class FundingServiceImpl implements FundingService {

	@Autowired
	private FundingReadDao fundingReadDao;

	@Autowired
	private FundingInvestorRelReadDao firReadDao;

	@Autowired
	private InvestorReadDao investorReadDao;
	@Autowired
	private FundingWriteDao fundingWriteDao;
	@Autowired
	private FundingInvestorRelWriteDao firWriteDao;

	@Override
	public List get(int companyId) {
		List<Funding> fundingList = fundingReadDao.getByCompanyId(companyId);
		List<FundingVO> fundingVOList = new ArrayList<FundingVO>();

		for (Funding funding : fundingList) {
			FundingVO fVO = new FundingVO();
			fVO.setFunding(funding);
			List<FundingInvestorRel> firList = firReadDao.get(funding.getId());
			List<FundingInvestorRelVO> fiVOList = new ArrayList<FundingInvestorRelVO>();
			for (FundingInvestorRel fir : firList) {
				FundingInvestorRelVO fiVO = new FundingInvestorRelVO();
				fiVO.setFir(fir);
				fiVO.setInvestor(investorReadDao.getById(fir.getInvestorId()));
				fiVOList.add(fiVO);
			}

			fVO.setFirList(fiVOList);
			fundingVOList.add(fVO);
		}

		return fundingVOList;
	}

	@Override
	public void addFundings(List fundings) {
		// TODO Auto-generated method stub

	}

	@Override
	public void deleteFundings(List<Integer> ids, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		if (ids == null || ids.isEmpty())
			return;
		for (Integer id : ids) {
			Funding funding = fundingReadDao.getById(id);
			funding.setActive('N');
			funding.setModifyTime(time);
			funding.setModifyUser(userId);
			fundingWriteDao.update(funding);
			List<FundingInvestorRel> firList = firReadDao.get(id);
			deleteFirs(firList, userId);
		}

	}

	@Override
	public void updateFunding(Funding funding) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		funding.setModifyTime(time);
		fundingWriteDao.update(funding);
	}

	@Override
	public void addFunding(Funding funding) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		funding.setCreateTime(time);
		funding.setActive('Y');
		fundingWriteDao.insert(funding);
	}

	@Override
	public void addFirs(List<FundingInvestorRel> firList, Integer userId) {
		if (firList == null || firList.isEmpty())
			return;
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for (FundingInvestorRel fir : firList) {
			fir.setActive('Y');
			fir.setCreateTime(time);
			fir.setCreateUser(userId);
			firWriteDao.insert(fir);
		}

	}

	@Override
	public void deleteFirs(List<FundingInvestorRel> firList, Integer userId) {
		if (firList == null || firList.isEmpty())
			return;
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for (FundingInvestorRel fir : firList) {
			fir.setActive('N');
			fir.setCreateTime(time);
			fir.setModifyUser(userId);
			fir.setModifyTime(time);
			firWriteDao.update(fir);
		}

	}

	@Override
	public void addFundingAndFirList(Funding funding, List<FundingInvestorRel> firList, Integer userId) {
		addFunding(funding);
		if (firList == null || firList.isEmpty())
			return;
		Integer fundingId = funding.getId();
		for (FundingInvestorRel fir : firList) {
			fir.setFundingId(fundingId);
		}
		addFirs(firList, userId);
	}

}
