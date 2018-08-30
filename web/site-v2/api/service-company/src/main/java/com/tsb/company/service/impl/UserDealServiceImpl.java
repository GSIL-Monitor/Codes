package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.UserDealService;
import com.tsb.company.vo.DealNoteVO;
import com.tsb.company.vo.DealUserScoreVO;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.DealNoteReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.UserOrganizationRelReadDao;
import com.tsb.dao.read.org.user.DealUserScoreReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.write.org.ColdcallCompanyRelWriteDao;
import com.tsb.dao.write.org.DealNoteWriteDao;
import com.tsb.dao.write.org.DealWriteDao;
import com.tsb.dao.write.org.user.DealUserRelWriteDao;
import com.tsb.dao.write.org.user.DealUserScoreWriteDao;
import com.tsb.enums.DealDeclineStatus;
import com.tsb.enums.DealPriority;
import com.tsb.enums.DealStatus;
import com.tsb.enums.DealType;
import com.tsb.enums.UserIdentify;
import com.tsb.model.org.ColdcallCompanyRel;
import com.tsb.model.org.Deal;
import com.tsb.model.org.UserOrganizationRel;
import com.tsb.model.org.user.DealNote;
import com.tsb.model.org.user.DealUserRel;
import com.tsb.model.org.user.DealUserScore;
import com.tsb.model.user.User;

@Service
public class UserDealServiceImpl implements UserDealService {
	@Autowired
	private DealReadDao dealReadDao;
	@Autowired
	private DealWriteDao dealWriteDao;
	@Autowired
	private UserOrganizationRelReadDao userOrgRelReadDao;
	@Autowired
	private DealUserRelWriteDao dealUserRelWriteDao;
	@Autowired
	private DealUserScoreReadDao dealUserScoreReadDao;
	@Autowired
	private DealUserScoreWriteDao dealUserScoreWriteDao;
	@Autowired
	private DealNoteReadDao dealNoteReadDao;
	@Autowired
	private DealNoteWriteDao dealNoteWriteDao;
	@Autowired
	private UserReadDao userReadDao;
	@Autowired
	private ColdcallCompanyRelWriteDao coldcallCompanyRelWriteDao;
	@Autowired
	private CompanyReadDao companyReadDao;

	@SuppressWarnings("rawtypes")
	@Override
	public List getRelDeals(Integer userId) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public DealNote getDealNote(Integer userId) {
		// TODO Auto-generated method stub
		return null;
	}

	@Override
	public void createNewDeal(Integer userId, Integer companyId, Integer score) {

		UserOrganizationRel userOrgRel = userOrgRelReadDao.get(userId);
		Deal newDeal = new Deal();
		newDeal.setCompanyId(companyId);
		newDeal.setOrganizationId(userOrgRel.getOrganizationId());
		// default hot,20030
		newDeal.setPriority(DealPriority.HOT.getValue());
		// default deal type is user,23010
		newDeal.setType(DealType.USER.getValue());
		// default dealStatus is new deal,19010
		newDeal.setStatus(DealStatus.NEWDEAL.getValue());
		newDeal.setCurrency(0);
		// default dealDeclineStatus is normal,18010
		newDeal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
		if (score == 4) {
			// 20030
			newDeal.setPriority(DealPriority.HOT.getValue());
			// 18010
			newDeal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
		} else if (score == 3) {
			// 20020
			newDeal.setPriority(DealPriority.WARM.getValue());
			// 18010
			newDeal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
		} else if (score == 2) {
			// 20010
			newDeal.setPriority(DealPriority.COLD.getValue());
			// 18020
			newDeal.setDeclineStatus(DealDeclineStatus.DECLINE.getValue());
		} else {
			// 20010
			newDeal.setPriority(DealPriority.COLD.getValue());
			// 18015
			newDeal.setDeclineStatus(DealDeclineStatus.ARCHIVE.getValue());
		}
		// create a new deal
		dealWriteDao.insert(newDeal);

		newDeal = dealReadDao.getByOrganization(companyId, userOrgRel.getOrganizationId());
		// 在deal_user_rel新增一条记录
		addDealUserRel(userId, newDeal.getId());

	}

	@Override
	public void addDealScore(Integer userId, Integer dealId) {
		// TODO Auto-generated method stub
	}

	@Override
	public void addDealNote(Integer userId, Integer dealId) {
		// TODO Auto-generated method stub

	}

	@Override
	public void updateDealScore(Integer userId, Integer dealId) {
		// TODO Auto-generated method stub

	}

	@Override
	public void updateDealNote(Integer userId, Integer dealId) {
		// TODO Auto-generated method stub

	}

	@Override
	public void deleteDealNote(Integer userId, Integer dealId) {
		// TODO Auto-generated method stub

	}

	@Override
	public void modifyDealScore(Integer userId, Integer companyId, Integer score, Integer type) {
		// check deal exits
		Deal deal = getDealByUserIdAndCompanyId(userId, companyId);
		if (null == deal) {
			createNewDeal(userId, companyId, score);

			UserOrganizationRel userOrgRel = userOrgRelReadDao.get(userId);
			Deal newDeal = dealReadDao.getByOrganization(companyId, userOrgRel.getOrganizationId());

			addDealScore(userId, newDeal.getId(), score, type);

		} else {
			if (score == 4) {
				// 18010
				deal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
				// 20030
				deal.setPriority(DealPriority.HOT.getValue());
			} else if (score == 3) {
				// 18010
				deal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
				// 20020
				deal.setPriority(DealPriority.WARM.getValue());
			} else if (score == 2) {
				// 18020
				deal.setDeclineStatus(DealDeclineStatus.DECLINE.getValue());
				// 20010
				deal.setPriority(DealPriority.COLD.getValue());

			} else {
				// 18015
				deal.setDeclineStatus(DealDeclineStatus.ARCHIVE.getValue());
				// 20010
				deal.setPriority(DealPriority.COLD.getValue());
			}

			dealWriteDao.update(deal);

			DealUserScore dealUserScore = dealUserScoreReadDao.getByUserIdAndDealId(userId, deal.getId());
			if (null == dealUserScore) {
				addDealScore(userId, deal.getId(), score, type);
			} else {
				// update
				dealUserScore.setScore(score);
				dealUserScore.setType(type);
				dealUserScoreWriteDao.update(dealUserScore);
			}
		}
	}

	@Override
	public List<DealUserScoreVO> getDealUserScore(Integer userId, Integer companyId) {
		Deal deal = getDealByUserIdAndCompanyId(userId, companyId);
		List<DealUserScoreVO> dealUserScoreVOList = new ArrayList<DealUserScoreVO>();
		if (null != deal) {
			List<DealUserScore> dealUserScoreList = dealUserScoreReadDao.listByDealId(deal.getId());
			if (null != dealUserScoreList && !dealUserScoreList.isEmpty()) {
				for (DealUserScore dealUserScore : dealUserScoreList) {
					DealUserScoreVO dealUserScoreVO = new DealUserScoreVO();

					dealUserScoreVO.setScore(dealUserScore.getScore());
					dealUserScoreVO.setOwner(dealUserScore.getUserId() == userId);
					// username
					User user = userReadDao.getById(dealUserScore.getUserId());
					dealUserScoreVO.setUserName(user.getUsername());

					dealUserScoreVOList.add(dealUserScoreVO);
				}
			}

		}
		return dealUserScoreVOList;
	}

	@Override
	public List<DealNoteVO> getDealNote(Integer userId, String code) {
		Integer companyId = companyReadDao.getIdByCode(code);
		Deal deal = getDealByUserIdAndCompanyId(userId, companyId);
		List<DealNoteVO> dealNoteVOList = new ArrayList<DealNoteVO>();
		if (null != deal) {
			// 组织内,note任何人都可见
			List<DealNote> dealNotes = dealNoteReadDao.getDealNotes(deal.getId());
			if (dealNotes != null && !dealNotes.isEmpty()) {
				for (DealNote dealNote : dealNotes) {
					DealNoteVO dealNoteVO = new DealNoteVO();

					dealNoteVO.setDealNote(dealNote);
					dealNoteVO.setOwner(dealNote.getUserId() == userId);
					User user = userReadDao.getById(dealNote.getUserId());
					dealNoteVO.setUserName(user.getUsername());
					dealNoteVOList.add(dealNoteVO);
				}
			}
		}
		return dealNoteVOList;
	}

	@Override
	public void modifyDealNote(Integer userId, String code, Integer noteId, String note) {
		Integer companyId = companyReadDao.getIdByCode(code);
		if (null != noteId) {
			updateDealNote(noteId, note);
		}
		// 新建deal note
		else {
			// check deal exits
			Deal deal = getDealByUserIdAndCompanyId(userId, companyId);
			if (null == deal) {
				createNewDeal(userId, companyId, 4); // priority as hot

				UserOrganizationRel userOrgRel = userOrgRelReadDao.get(userId);
				Deal newDeal = dealReadDao.getByOrganization(companyId, userOrgRel.getOrganizationId());

				addDealNote(userId, newDeal.getId(), note);
			} else {
				addDealNote(userId, deal.getId(), note);
			}
		}

	}

	protected void addDealScore(Integer userId, Integer dealId, Integer score, Integer type) {
		DealUserScore dealUserScore = new DealUserScore();
		dealUserScore.setUserId(userId);
		dealUserScore.setDealId(dealId);
		dealUserScore.setScore(score);
		dealUserScore.setType(type);
		dealUserScoreWriteDao.insert(dealUserScore);

	}

	protected void addDealUserRel(Integer userId, Integer dealId) {
		// 在表deal_user_rel中插入一条user和deal关联的数据
		DealUserRel dealUserRel = new DealUserRel();
		dealUserRel.setDealId(dealId);
		dealUserRel.setUserId(userId);
		// 21020
		dealUserRel.setUserIdentify(UserIdentify.ASSIGNEE.getValue());
		// 用户自选,23010
		dealUserRel.setType(DealType.USER.getValue());
		dealUserRelWriteDao.insert(dealUserRel);
	}

	protected void addDealNote(Integer userId, Integer dealId, String note) {
		DealNote dealNote = new DealNote();
		dealNote.setUserId(userId);
		dealNote.setDealId(dealId);
		dealNote.setNote(note);
		dealNoteWriteDao.insert(dealNote);
	}

	protected void updateDealNote(Integer noteId, String note) {
		DealNote dealNote = dealNoteReadDao.get(noteId);
		dealNote.setNote(note);
		dealNoteWriteDao.update(dealNote);
	}

	protected Deal getDealByUserIdAndCompanyId(Integer userId, Integer companyId) {
		// organization和user 一对一对情况
		UserOrganizationRel userOrgRelList = userOrgRelReadDao.get(userId);
		Deal deal = dealReadDao.getByOrganization(companyId, userOrgRelList.getOrganizationId());
		return deal;
	}

	@Override
	public void deleteDealNote(Integer noteId) {
		dealNoteWriteDao.delete(noteId);

	}

	@Override
	public void addDeal(Integer companyId, Integer orgId, Integer userId, Integer coldcallId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Deal deal = new Deal();
		deal.setCompanyId(companyId);
		deal.setOrganizationId(orgId);
		// 18010
		deal.setDeclineStatus(DealDeclineStatus.NORMAL.getValue());
		// 19010
		deal.setStatus(DealStatus.NEWDEAL.getValue());
		// 20030
		deal.setPriority(DealPriority.HOT.getValue());
		deal.setCurrency(0);
		deal.setCreateTime(time);
		dealWriteDao.insert(deal);

		DealUserRel dur = new DealUserRel();
		dur.setUserId(userId);
		dur.setDealId(deal.getId());
		// 21020
		dur.setUserIdentify(UserIdentify.ASSIGNEE.getValue());
		if (coldcallId > 0) {
			// 23020
			dur.setType(DealType.COLDCALL.getValue());
		} else {
			// 23010
			dur.setType(DealType.USER.getValue());
		}
		dur.setCreateTime(time);
		dealUserRelWriteDao.insert(dur);

		DealUserScore dus = new DealUserScore();
		dus.setUserId(userId);
		dus.setDealId(deal.getId());
		dus.setType(22010);
		dus.setScore(4);
		dus.setCreateTime(time);
		dealUserScoreWriteDao.insert(dus);

		if (coldcallId > 0) {
			ColdcallCompanyRel ccr = new ColdcallCompanyRel();
			ccr.setColdcallId(coldcallId);
			ccr.setCompanyId(companyId);
			ccr.setCreateTime(time);
			coldcallCompanyRelWriteDao.insert(ccr);
		}

	}
}
