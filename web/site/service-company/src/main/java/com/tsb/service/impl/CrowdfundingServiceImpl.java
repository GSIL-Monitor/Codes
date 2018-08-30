package com.tsb.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.dao.read.crowdfunding.CrowdfundingReadDao;
import com.tsb.dao.read.crowdfunding.SourceCfDocumentReadDao;
import com.tsb.dao.read.crowdfunding.SourceCfLeaderReadDao;
import com.tsb.dao.read.crowdfunding.SourceCfMemberReadDao;
import com.tsb.dao.read.crowdfunding.SourceCrowdfundingReadDao;
import com.tsb.model.crowdfunding.Crowdfunding;
import com.tsb.model.crowdfunding.SourceCfDocument;
import com.tsb.model.crowdfunding.SourceCfLeader;
import com.tsb.model.crowdfunding.SourceCfMember;
import com.tsb.model.crowdfunding.SourceCrowdfunding;
import com.tsb.model.vo.CfDBVO;
import com.tsb.model.vo.CfHeadVO;
import com.tsb.model.vo.CrowdfundingVO;
import com.tsb.service.CrowdfundingService;

@Service
public class CrowdfundingServiceImpl implements CrowdfundingService {
	@Autowired
	private CrowdfundingReadDao cfReadDao;
	@Autowired
	private SourceCrowdfundingReadDao scfReadDao;
	@Autowired
	private SourceCfDocumentReadDao sCfDocumentReadDao;
	@Autowired
	private SourceCfLeaderReadDao scfLeaderReadDao;
	@Autowired
	private SourceCfMemberReadDao scfMemberReadDao;

	@Override
	public CrowdfundingVO getById(Integer cfId) {
		CrowdfundingVO crowdfundingVO = new CrowdfundingVO();

		Crowdfunding crowdfunding = cfReadDao.getById(cfId);
		SourceCrowdfunding sourceCrowdfunding = scfReadDao.getBycfId(crowdfunding.getId());
		List<SourceCfDocument> sourceCfDocumentList = sCfDocumentReadDao.getBySourceCfId(sourceCrowdfunding.getId());
		List<SourceCfLeader> sourceCfLeaderList = scfLeaderReadDao.getBySourceCfId(sourceCrowdfunding.getId());
		crowdfundingVO.setCrowdfunding(crowdfunding);
		crowdfundingVO.setSourceCrowdfunding(sourceCrowdfunding);
		crowdfundingVO.setSourceCfDocumentList(sourceCfDocumentList);
		crowdfundingVO.setSourceCfLeaderList(sourceCfLeaderList);

		return crowdfundingVO;
	}

	@Override
	public List<SourceCrowdfunding> getByPage(int page, int status, int source) {
		if (status == 0 && source == 0)
			return cfReadDao.getByPage((page - 1) * 20);
		else if (status == 0)
			return cfReadDao.getBySource((page - 1) * 20, source);
		else if (source == 0)
			return cfReadDao.getByStatus((page - 1) * 20, status);
		else {
			CfDBVO cf = new CfDBVO();
			cf.setSource(source);
			cf.setStart((page - 1) * 20);
			cf.setStatus(status);
			return cfReadDao.getByStatusAndSource(cf);
		}

	}

	@Override
	public int count(int status, int source) {
		if (status == 0 && source == 0)
			return cfReadDao.count();
		else if (status == 0)
			return cfReadDao.countBySource(source);
		else if (source == 0)
			return cfReadDao.countByStatus(status);
		else
			return cfReadDao.countByStatusAndSource(status, source);
	}

	@Override
	public CfHeadVO getCfHeadVOInfo(Integer scfId) {
		CfHeadVO cfHeadVO = scfReadDao.getCfHeadInfo(scfId);
		cfHeadVO.setScfLeaderCount(scfLeaderReadDao.count(scfId));
		cfHeadVO.setScfMemberCount(scfMemberReadDao.count(scfId));
		return cfHeadVO; 
	}

	@Override
	public List<SourceCfMember> getMembers(Integer scfId) {
		
		return scfMemberReadDao.getMembers(scfId);
	}

}
