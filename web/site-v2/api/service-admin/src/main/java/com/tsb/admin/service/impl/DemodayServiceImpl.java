package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.DemodayVOReadDao;
import com.tsb.admin.service.DemodayService;
import com.tsb.admin.vo.AvgPreScoreVO;
import com.tsb.admin.vo.DemodayCompanyVO;
import com.tsb.admin.vo.DemodayDetailVO;
import com.tsb.admin.vo.DemodayOrgVO;
import com.tsb.admin.vo.UserPreScoreVO;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.demoday.DemodayCompanyReadDao;
import com.tsb.dao.read.demoday.DemodayOrganizationReadDao;
import com.tsb.dao.read.demoday.DemodayReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.write.demoday.DemodayCompanyWriteDao;
import com.tsb.dao.write.demoday.DemodayOrganizationWriteDao;
import com.tsb.dao.write.demoday.DemodayPreScoreWriteDao;
import com.tsb.dao.write.demoday.DemodayResultWriteDao;
import com.tsb.dao.write.demoday.DemodayScoreWriteDao;
import com.tsb.dao.write.demoday.DemodayWriteDao;
import com.tsb.enums.DemodayCompanyStatus;
import com.tsb.enums.DemodayJoin;
import com.tsb.enums.DemodayStatus;
import com.tsb.model.demoday.Demoday;
import com.tsb.model.demoday.DemodayCompany;
import com.tsb.model.demoday.DemodayOrganization;

@Service
public class DemodayServiceImpl implements DemodayService {
	@Autowired
	private DemodayReadDao demodayReadDao;
	@Autowired
	private DemodayWriteDao demodayWriteDao;
	@Autowired
	private OrganizationReadDao orgReadDao;
	@Autowired
	private DemodayOrganizationReadDao demodayOrgReadDao;
	@Autowired
	private DemodayOrganizationWriteDao demodayOrgWriteDao;
	@Autowired
	private DemodayVOReadDao demodayVOReadDao;
	@Autowired
	private CompanyReadDao companyReadDao;
	@Autowired
	private DemodayCompanyReadDao demodayCompanyReadDao;
	@Autowired
	private DemodayCompanyWriteDao demodayCompanyWriteDao;
	@Autowired
	private DemodayPreScoreWriteDao   demodayPreScoreWriteDao;
	@Autowired
	private DemodayScoreWriteDao   demodayScoreWriteDao;
	@Autowired
	private DemodayResultWriteDao   demodayResultWriteDao;


	@Override
	public Demoday getByName(String name) {

		return demodayReadDao.getByName(name);
	}

	@Override
	public void addDemoday(Demoday demoday, List<Integer> orgIds) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		demoday.setCreateTime(time);
		demoday.setStatus(DemodayStatus.SUBMMITTING.getValue());
		demodayWriteDao.insert(demoday);
		Integer demodayId = demoday.getId();
		for (Integer orgId : orgIds) {
			DemodayOrganization demodayOrg = new DemodayOrganization();
			demodayOrg.setOrganizationId(orgId);
			demodayOrg.setDemodayId(demodayId);
			demodayOrg.setCreateTime(time);
			// 默认新加的都是参加
			demodayOrg.setStatus(DemodayJoin.JOIN.getValue());

			demodayOrgWriteDao.insert(demodayOrg);
		}
	}

	@Override
	public void updateDemoday(Demoday demoday) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		demoday.setModifyTime(time);
		demodayWriteDao.update(demoday);
		Integer status = demoday.getStatus();
		List<DemodayCompany> demodayCompanies = demodayCompanyReadDao.getByDemodayId(demoday.getId());

		if (DemodayStatus.SUBMMITTING.getValue() == status || DemodayStatus.SUBMIT_END.getValue() == status) {
			updateDemodayCompanies(demodayCompanies, null);
		} else if (DemodayStatus.PRESCORING.getValue() == status || DemodayStatus.PRESCORE_DONE.getValue() == status) {
			updateDemodayCompanies(demodayCompanies, DemodayCompanyStatus.PRESCORING.getValue());
		} else if (DemodayStatus.CONNECTTING_TEAM.getValue() == status
				|| DemodayStatus.CONNECTTING_TEAM_DONE.getValue() == status) {
			updateDemodayCompaniesJoinStatus(demodayCompanies, DemodayJoin.CONNECTING.getValue());
		} else if (DemodayStatus.OPENING.getValue() == status) {
			updateDemodayCompanies(demodayCompanies, DemodayCompanyStatus.SCORING.getValue());
		} else if (DemodayStatus.DONE.getValue() == status) {
			updateDemodayCompanies(demodayCompanies, DemodayCompanyStatus.SCORE_DONE.getValue());
		}
	}

	protected void updateDemodayCompaniesJoinStatus(List<DemodayCompany> demodayCompanies, Integer joinStatus) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for (DemodayCompany demodayCompany : demodayCompanies) {
			// 初筛通过才联络，否则为null
			if (null!=demodayCompany.getScoringStatus()&&demodayCompany.getScoringStatus() == DemodayCompanyStatus.PRESCORE_PAAS.getValue()) {
				demodayCompany.setJoinStatus(joinStatus);
				demodayCompany.setModifyTime(time);
				demodayCompanyWriteDao.update(demodayCompany);
			} else {
				demodayCompany.setJoinStatus(null);
				demodayCompany.setModifyTime(time);
				demodayCompanyWriteDao.update(demodayCompany);
			}
		}
	}

	protected void updateDemodayCompanies(List<DemodayCompany> demodayCompanies, Integer scoringStatus) {

		for (DemodayCompany demodayCompany : demodayCompanies) {
			// 项目提交
			if (null == scoringStatus) {
				updateDemodayCompany(demodayCompany, scoringStatus);
			}
			// 打分、结束
			else if (scoringStatus == DemodayCompanyStatus.SCORING.getValue()
					|| scoringStatus == DemodayCompanyStatus.SCORE_DONE.getValue()) {
				if (null!=demodayCompany.getJoinStatus()&&demodayCompany.getJoinStatus() == DemodayJoin.JOIN.getValue()
						&& demodayCompany.getScoringStatus() == DemodayCompanyStatus.PRESCORE_PAAS.getValue()) {
					updateDemodayCompany(demodayCompany, scoringStatus);
				}
			} else {
				// 其他
				updateDemodayCompany(demodayCompany, scoringStatus);
			}
		}
	}

	protected void updateDemodayCompany(DemodayCompany demodayCompany, Integer scoringStatus) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		demodayCompany.setScoringStatus(scoringStatus);
		demodayCompany.setModifyTime(time);
		demodayCompanyWriteDao.update(demodayCompany);
	}

	@SuppressWarnings("rawtypes")
	@Override
	public List getXOrgList(Integer status) {

		return orgReadDao.getXOrgs(status);
	}

	@Override
	public DemodayDetailVO getDemodayDetai(Integer demodayId) {
		Demoday demoday = demodayReadDao.get(demodayId);
		DemodayDetailVO demodayDetailVO = new DemodayDetailVO();
		demodayDetailVO.setDemoday(demoday);
		List<DemodayOrgVO> demodayOrgs = demodayVOReadDao.getDemodayOrgVOList(demodayId);
		demodayDetailVO.setDemodayOrgs(demodayOrgs);
		List<DemodayCompanyVO> demodayCompanies = demodayVOReadDao.getDemodayCompanyVOList(demodayId);
		demodayDetailVO.setDemodayCompanies(demodayCompanies);
		return demodayDetailVO;
	}

	@Override
	public void updateDemodayOrg(Integer demodayId, Integer orgId, Integer status) {
		DemodayOrganization demodayOrg = demodayOrgReadDao.getDemodayOrg(demodayId, orgId);
		demodayOrg.setStatus(status);
		demodayOrgWriteDao.update(demodayOrg);

	}

	@Override
	public void updateDemodayOrg(Integer demodayId, List<Integer> orgIds, Integer status) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for (Integer orgId : orgIds) {
			DemodayOrganization demodayOrg = demodayOrgReadDao.getDemodayOrg(demodayId, orgId);
			if (null != demodayOrg) {
				demodayOrg.setStatus(status);
				demodayOrgWriteDao.update(demodayOrg);
			} else {

				DemodayOrganization newDemodayOrg = new DemodayOrganization();
				newDemodayOrg.setOrganizationId(orgId);
				newDemodayOrg.setDemodayId(demodayId);
				newDemodayOrg.setCreateTime(time);
				// 默认新加的都是参加
				newDemodayOrg.setStatus(status);
				demodayOrgWriteDao.insert(newDemodayOrg);
			}

		}

	}

	@Override
	public void updateDemodayCompanies(Integer demodayId, List<DemodayCompanyVO> demodayCompanyVOList) {
		Timestamp time = new Timestamp(System.currentTimeMillis());

		for (DemodayCompanyVO vo : demodayCompanyVOList) {
			Integer companyId = companyReadDao.getByCode(vo.getCode()).getId();
			DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);

			demodayCompany.setJoinStatus(vo.getJoinStatus());
			demodayCompany.setScoringStatus(vo.getScoringStatus());
			demodayCompany.setModifyTime(time);

			demodayCompanyWriteDao.update(demodayCompany);

		}
	}

	@Override
	public Demoday get(Integer demodayId) {

		return demodayReadDao.get(demodayId);
	}

	@Override
	public List<DemodayOrgVO> getDemodayOrgs(Integer demodayId) {
		return demodayVOReadDao.getDemodayOrgVOList(demodayId);
	}

	@Override
	public List<DemodayCompanyVO> getDemodayCompanies(Integer demodayId) {
		return demodayVOReadDao.getDemodayCompanyVOList(demodayId);
	}

	@Override
	public List<AvgPreScoreVO> getCompanyAvgPreScore(Integer demodayId) {

		List<AvgPreScoreVO> avgPreScoreVOList = demodayVOReadDao.getCompaniesAvgPreScore(demodayId);
		if (null != avgPreScoreVOList && !avgPreScoreVOList.isEmpty()) {
			for (AvgPreScoreVO avgPreScore : avgPreScoreVOList) {

				// 所有合伙人打分
				List<UserPreScoreVO> partnerPreScore = demodayVOReadDao
						.getPartnerPreScores(avgPreScore.getDemodayCompanyId());
				avgPreScore.setPartnerPreScores(partnerPreScore);
			}
		}
		return avgPreScoreVOList;

	}

	@Override
	public List<UserPreScoreVO> getAllUserPreScore(Integer dealDemodayId) {

		return demodayVOReadDao.getAllUserPreScores(dealDemodayId);
	}

	@Override
	public void updateDemodayCompany(Integer id, Integer scoringStatus) {
		DemodayCompany demodayCompany = demodayCompanyReadDao.getById(id);
		demodayCompany.setScoringStatus(scoringStatus);
		demodayCompanyWriteDao.update(demodayCompany);

	}

	@Override
	public void updateDemodayCompany(List<Integer> ids, Integer scoringStatus) {
		for (Integer id : ids) {
			updateDemodayCompany(id, scoringStatus);
		}
	}

	@Override
	public void updateDemodayCompanyJoinStatus(List<Integer> ids, Integer joinStatus) {
		for (Integer id : ids) {
			DemodayCompany demodayCompany = demodayCompanyReadDao.getById(id);
			demodayCompany.setJoinStatus(joinStatus);
			demodayCompanyWriteDao.update(demodayCompany);
		}

	}

	@Override
	public void removeDemodayCompany(Integer id) {
	
		demodayPreScoreWriteDao.delete(id);
		demodayScoreWriteDao.delete(id);
		demodayResultWriteDao.delete(id);	
		demodayCompanyWriteDao.delete(id);
	}

	@Override
	/**
	 * 获取烯牛快跑推荐的项目
	 * **/
	public List<DemodayCompanyVO> getSysDemodayCompanies(Integer demodayId, Integer start, Integer pageSize,String orgName) {
		Integer orgId = orgReadDao.getOrgByName(orgName).getId();
		return demodayVOReadDao.getSysDemodayCompanyVOList(demodayId,start,pageSize,orgId);
	}

	@Override
	public void updateSysDemodayCompanies(List<Integer> ids, Character pass) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for(Integer id : ids){
			DemodayCompany demodayCompany =demodayCompanyReadDao.getById(id);
			demodayCompany.setPass(pass);
			demodayCompany.setModifyTime(time);
			demodayCompanyWriteDao.update(demodayCompany);
		}
		
	}

	@Override
	public List<DemodayCompanyVO> getSysDemodayCompanies(Integer demodayId, String orgName) {
		Integer orgId = orgReadDao.getOrgByName(orgName).getId();
		return demodayVOReadDao.getAllSysDemodayCompanyVO(demodayId,orgId);
	}

}
