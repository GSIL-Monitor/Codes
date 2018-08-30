package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.dao.DemodayVODao;
import com.tsb.company.service.DemodayService;
import com.tsb.company.vo.DemodayAllUserScoreVO;
import com.tsb.company.vo.DemodayCompanyVO;
import com.tsb.company.vo.DemodayOrgResultVO;
import com.tsb.company.vo.DemodayResultVO;
import com.tsb.company.vo.DemodayVO;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.demoday.DemodayCompanyReadDao;
import com.tsb.dao.read.demoday.DemodayOrganizationReadDao;
import com.tsb.dao.read.demoday.DemodayPreScoreReadDao;
import com.tsb.dao.read.demoday.DemodayReadDao;
import com.tsb.dao.read.demoday.DemodayResultReadDao;
import com.tsb.dao.read.demoday.DemodayScoreReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.user.UserRoleReadDao;
import com.tsb.dao.write.demoday.DemodayCompanyWriteDao;
import com.tsb.dao.write.demoday.DemodayOrganizationWriteDao;
import com.tsb.dao.write.demoday.DemodayPreScoreWriteDao;
import com.tsb.dao.write.demoday.DemodayResultWriteDao;
import com.tsb.dao.write.demoday.DemodayScoreWriteDao;
import com.tsb.enums.DemodayJoin;
import com.tsb.enums.DemodayStatus;
import com.tsb.model.demoday.Demoday;
import com.tsb.model.demoday.DemodayCompany;
import com.tsb.model.demoday.DemodayOrganization;
import com.tsb.model.demoday.DemodayPreScore;
import com.tsb.model.demoday.DemodayResult;
import com.tsb.model.demoday.DemodayScore;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class DemodayServiceImpl implements DemodayService {
	@Autowired
	private DemodayReadDao demodayReadDao;
	@Autowired
	private DemodayCompanyReadDao demodayCompanyReadDao;
	@Autowired
	private DemodayPreScoreReadDao demodayPreScoreReadDao;
	@Autowired
	private DemodayPreScoreWriteDao demodayPreScoreWriteDao;
	@Autowired
	private CompanyReadDao companyReadDao;
	@Autowired
	private OrganizationReadDao orgReadDao;
	@Autowired
	private DemodayScoreReadDao demodayScoreReadDao;
	@Autowired
	private DemodayScoreWriteDao demodayScoreWriteDao;
	@Autowired
	private DemodayResultReadDao demodayResultReadDao;
	@Autowired
	private DemodayResultWriteDao demodayResultWriteDao;
	@Autowired
	private DemodayVODao demodayVODao;
	@Autowired
	private UserRoleReadDao userRoleReadDao;
	@Autowired
	private DemodayOrganizationReadDao demodayOrgReadDao;
	@Autowired
	private DemodayOrganizationWriteDao demodayOrgWriteDao;
	@Autowired
	private DemodayCompanyWriteDao demodayCompanyWriteDao;

	@Override
	public DemodayVO getDemoday(Integer demodayId) {
		Demoday demoday = demodayReadDao.get(demodayId);
		List<DemodayCompany> demodayCompanies = demodayCompanyReadDao.getByDemodayId(demodayId);
		DemodayVO demodayVO = new DemodayVO();
		demodayVO.setDemoday(demoday);
		demodayVO.setDemodayCompanies(demodayCompanies);
		return demodayVO;
	}

	@Override
	public List<DemodayVO> get() {
		List<DemodayVO> demodayVOList = new ArrayList<DemodayVO>();
		List<Demoday> demodayList = demodayReadDao.getAll();
		if (null != demodayList && !demodayList.isEmpty()) {
			for (Demoday demoday : demodayList) {
				DemodayVO demodayVO = new DemodayVO();
				List<DemodayCompany> demodayCompanies = demodayCompanyReadDao.getByDemodayId(demoday.getId());
				demodayVO.setDemoday(demoday);
				demodayVO.setDemodayCompanies(demodayCompanies);
				demodayVOList.add(demodayVO);
			}
		}
		return demodayVOList;
	}

	@Override
	public Map getPrescore(Integer userId, Integer demodayId, String code) {

		Integer companyId = companyReadDao.getIdByCode(code);
		DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);
		DemodayPreScore demodayPrescore = demodayPreScoreReadDao.getDemodayPrescore(demodayCompany.getId(), userId);
		// 用户所在的组织
		Integer orgId = orgReadDao.getByUser(userId).getId();
		// 用户所在的组织是否来参加了此次demoday，参加了则demodayOrg不为null,28030代表参加
		DemodayOrganization demodayOrg = demodayOrgReadDao.getJoinDemodayOrg(demodayId, orgId,
				DemodayJoin.JOIN.getValue());
		Map map = new HashMap();
		// demoday status
		map.put("scoringStatus", demodayCompanyReadDao.getDemodayCompany(demodayId, companyId).getScoringStatus());
		// demoday_prescore score
		map.put("preScore", null != demodayPrescore ? demodayPrescore.getScore() : null);
		map.put("demodayUser", null != demodayOrg);
		// 找到所有非当前初筛选中的公司的demodaycompany
		List<DemodayCompany> list = demodayCompanyReadDao.getRidCompId(demodayId, companyId);
		// 存放尚未打分的公司id
		List<Integer> compIds = new ArrayList<Integer>();
		for (DemodayCompany ddCompany : list) {
			// 该company尚未打分
			if (null == demodayPreScoreReadDao.getDemodayPrescore(ddCompany.getId(), userId)) {
				compIds.add(ddCompany.getCompanyId());
			} else {
				continue;
			}
		}
		if (!compIds.isEmpty()) {
			String nextCode = companyReadDao.getById(compIds.get(0)).getCode();
			map.put("nextCode", nextCode);
			map.put("last", false);
		} else {
			map.put("nextCode", "");
			map.put("last", true);
		}
		return map;
	}

	@Override
	public List getPreScores(Integer userId, Integer demodayId) {
		Demoday demoday = demodayReadDao.get(demodayId);
		Integer status = demoday.getStatus();
		if (status <= DemodayStatus.PRESCORING.getValue()) {
			status = DemodayStatus.PRESCORING.getValue();
		} else {
			status = DemodayStatus.PRESCORE_DONE.getValue();
		}
		return demodayVODao.getPreScores(userId, demodayId, status);
	}

	@Override
	public Map getScore(Integer userId, Integer demodayId, String code) {
		Integer companyId = companyReadDao.getIdByCode(code);
		DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);
		DemodayScore demodayScore = demodayScoreReadDao.getDemodayScore(demodayCompany.getId(), userId);
		// 用户所在的组织
		Integer orgId = orgReadDao.getByUser(userId).getId();
		// 用户所在的组织是否来参加了此次demoday，参加了则demodayOrg不为null,28030代表参加
		DemodayOrganization demodayOrg = demodayOrgReadDao.getJoinDemodayOrg(demodayId, orgId,
				DemodayJoin.JOIN.getValue());
		Map map = new HashMap();
		// demoday status
		map.put("scoringStatus", demodayCompanyReadDao.getDemodayCompany(demodayId, companyId).getScoringStatus());
		map.put("demodayScore", demodayScore);
		// 用户所属组织id
		map.put("orgId", orgReadDao.getByUser(userId).getId());
		// 合伙人type为25030
		map.put("partner", null != userRoleReadDao.getByRole(userId, 25030));
		map.put("demodayUser", null != demodayOrg);

		return map;
	}

	@Override
	public List getScores(Integer userId, Integer demodayId) {
		return demodayVODao.getScores(userId, demodayId);
	}

	@Override
	public void preScore(Integer userId, Integer demodayId, String code, Integer score) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Integer dealDemodayId = getDemodayCompanyId(code, demodayId);
		DemodayPreScore demodayPrescore = demodayPreScoreReadDao.getDemodayPrescore(dealDemodayId, userId);

		if (null == demodayPrescore) {
			// insert
			DemodayPreScore prescore = new DemodayPreScore();
			prescore.setCreateTime(time);
			prescore.setScore(score);
			prescore.setUserId(userId);
			prescore.setDealDemodayId(dealDemodayId);

			demodayPreScoreWriteDao.insert(prescore);
		} else {
			// update
			demodayPrescore.setModifyTime(time);
			demodayPrescore.setScore(score);

			demodayPreScoreWriteDao.update(demodayPrescore);
		}
	}

	@Override
	public void score(Integer userId, Integer demodayId, String code, List<Integer> scores) {

		Timestamp time = new Timestamp(System.currentTimeMillis());
		// demoday_company id
		Integer dealDemodayId = getDemodayCompanyId(code, demodayId);
		DemodayScore demodayScore = demodayScoreReadDao.getDemodayScore(dealDemodayId, userId);
		if (null == demodayScore) {
			// insert
			DemodayScore newDemodayScore = new DemodayScore();
			newDemodayScore.setCreateTime(time);
			newDemodayScore.setDealDemodayId(dealDemodayId);
			newDemodayScore.setUserId(userId);

			newDemodayScore.setIndustry(scores.get(0));
			newDemodayScore.setTeam(scores.get(1));
			newDemodayScore.setProduct(scores.get(2));
			newDemodayScore.setGain(scores.get(3));
			newDemodayScore.setPreMoney(scores.get(4));

			demodayScoreWriteDao.insert(newDemodayScore);
		} else {
			// update
			demodayScore.setIndustry(scores.get(0));
			demodayScore.setTeam(scores.get(1));
			demodayScore.setProduct(scores.get(2));
			demodayScore.setGain(scores.get(3));
			demodayScore.setPreMoney(scores.get(4));
			demodayScore.setModifyTime(time);

			demodayScoreWriteDao.update(demodayScore);
		}

	}

	@Override
	public DemodayResultVO getResult(Integer userId, Integer demodayId, String code) {

		Integer companyId = companyReadDao.getIdByCode(code);
		DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);
		Integer id = demodayCompany.getId();

		List<DemodayOrgResultVO> orgResults = demodayVODao.getOrgResults(id, demodayId);
		List<DemodayAllUserScoreVO> scoreList = demodayVODao.getAllUserScore(companyId, id);

		DemodayResultVO demodayResultVO = new DemodayResultVO();
		demodayResultVO.setOrgResults(orgResults);
		demodayResultVO.setScoreList(scoreList);

		return demodayResultVO;
	}

	@Override
	public void invest(Integer userId, Integer demodayId, String code, Integer result) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Integer orgId = orgReadDao.getByUser(userId).getId();
		Integer demodayCompanyId = getDemodayCompanyId(code, demodayId);
		DemodayResult demodayResult = demodayResultReadDao.getDemodayResult(demodayCompanyId, orgId);
		if (null == demodayResult) {
			// insert
			DemodayResult newDemodayResult = new DemodayResult();
			newDemodayResult.setOrganizationId(orgId);
			newDemodayResult.setDemodayCompanyId(demodayCompanyId);
			newDemodayResult.setResult(result);
			newDemodayResult.setCreateUser(userId);
			newDemodayResult.setCreateTime(time);
			demodayResultWriteDao.insert(newDemodayResult);
		} else {
			// update
			demodayResult.setModifyTime(time);
			demodayResult.setModifyUser(userId);
			demodayResult.setResult(result);

			demodayResultWriteDao.update(demodayResult);
		}
	}

	protected Integer getDemodayCompanyId(String code, Integer demodayId) {
		Integer companyId = companyReadDao.getIdByCode(code);
		DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);
		return demodayCompany.getId();
	}

	@Override
	public void updateDemodayOrgList(Integer demodayId, Integer status, List<String> orgNames) {
		Timestamp time = new Timestamp(System.currentTimeMillis());

		List<Integer> orgIds = orgReadDao.getIdsByNames(orgNames);
		if (status == DemodayJoin.JOIN.getValue()) {
			for (Integer orgId : orgIds) {
				DemodayOrganization oldDemodayOrg = demodayOrgReadDao.getDemodayOrg(demodayId, orgId);
				if (null == oldDemodayOrg) {
					// insert
					DemodayOrganization demodayOrg = new DemodayOrganization();
					demodayOrg.setDemodayId(demodayId);
					demodayOrg.setOrganizationId(orgId);
					demodayOrg.setStatus(status);
					demodayOrg.setCreateTime(time);
					demodayOrgWriteDao.insert(demodayOrg);
				} else {
					// update
					oldDemodayOrg.setModifyTime(time);
					oldDemodayOrg.setStatus(status);
					demodayOrgWriteDao.update(oldDemodayOrg);
				}
			}
		}

		else {
			// 不参加
			for (Integer orgId : orgIds) {
				DemodayOrganization oldDemodayOrg = demodayOrgReadDao.getDemodayOrg(demodayId, orgId);
				oldDemodayOrg.setStatus(status);
				oldDemodayOrg.setModifyTime(time);
				demodayOrgWriteDao.update(oldDemodayOrg);
			}
		}

	}

	@Override
	public Map getDemodayOrgs(Integer demodayId) {
		Map map = new HashMap();
		//28030
		map.put("join", demodayVODao.getJoinDemodayOrgs(demodayId, DemodayJoin.JOIN.getValue()));
		map.put("notJoin", demodayVODao.getNotJoinOrgs(demodayId, DemodayJoin.JOIN.getValue()));
		return map;
	}

	@Override
	public List<DemodayCompanyVO> getDemodayCompanies(Integer demodayId) {
		// demody中的所有公司，包括参加和不参加的
		return demodayVODao.getDemodayCompanies(demodayId);
	}

	@Override
	public Integer addDemodayCompany(Integer demodayId, String code, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Integer companyId = companyReadDao.getIdByCode(code);
		if (null != demodayCompanyReadDao.getDemodayCompany(demodayId, companyId)) {
			// 已经提交过的项目
			return -1;
		} else {

			DemodayCompany dc = new DemodayCompany();
			dc.setDemodayId(demodayId);
			dc.setCompanyId(companyId);
			dc.setOrganizationId(orgReadDao.getByUser(userId).getId());
			dc.setCreateTime(time);
			demodayCompanyWriteDao.insert(dc);
			return 0;
		}
	}

	@Override
	public Integer commitDemodayCompany(DemodayCompany demodayCompany, Integer userId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		DemodayCompany oldDemodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayCompany.getDemodayId(),
				demodayCompany.getCompanyId());
		if (null != oldDemodayCompany) {
			return -1;
		} else {
			demodayCompany.setCreateTime(time);

			demodayCompany.setOrganizationId(orgReadDao.getByUser(userId).getId());
			demodayCompanyWriteDao.insert(demodayCompany);
			return 0;
		}

	}

	@Override
	public Map getDemodayCompany(Integer demodayId, Integer companyId, Integer userId) {
		DemodayCompany demodayCompany = demodayCompanyReadDao.getDemodayCompany(demodayId, companyId);
		Map result = new HashMap();
		result.put("demodayCompany", demodayCompany);
		result.put("commitOrg", demodayCompany == null ? false
				: demodayCompany.getOrganizationId() == orgReadDao.getByUser(userId).getId());
		return result;
	}

	@Override
	public void updateDemodayCompany(DemodayCompany demodayCompany) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		demodayCompany.setModifyTime(time);
		demodayCompanyWriteDao.update(demodayCompany);

	}

	@Override
	public List notPassedList(Integer start, Integer pageSize, Integer userId, Integer demodayId) {
		return demodayVODao.getNotPassedList(start, pageSize, userId, demodayId);
	}

	@Override
	public int countNotPassNum(Integer demodayId) {
		return demodayCompanyReadDao.getNotPassNum(demodayId);
	}

}
