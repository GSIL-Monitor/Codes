package com.tsb.service.impl;

import java.sql.Timestamp;
import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.model.dict.ListStatus;
import com.tsb.model.user.CompanyList;
import com.tsb.model.user.CompanyListRel;
import com.tsb.model.user.UserCompanyListRel;
import com.tsb.service.UserListService;
import com.tsb.user.dao.read.CompanyListReadDao;
import com.tsb.user.dao.read.CompanyListRelReadDao;
import com.tsb.user.dao.read.UserCompanyListRelReadDao;
import com.tsb.user.dao.write.CompanyListWriteDao;
import com.tsb.user.dao.write.UserCompanyListRelWriteDao;
import com.tsb.user.model.vo.CompanyListVO;
import com.tsb.user.model.vo.UserList;

@Service
@SuppressWarnings("rawtypes")
public class UserListServiceImpl implements UserListService {
	@Autowired
	private UserCompanyListRelReadDao uclReadDao;
	@Autowired
	private CompanyListReadDao clReadDao;
	@Autowired
	private CompanyListRelReadDao clrReadDao;
	@Autowired
	private CompanyListWriteDao clWriteDao;
	@Autowired
	private UserCompanyListRelWriteDao uclrWriteDao;

	@Override
	public UserList getUserList(Integer userId, int page) {

		// clIds is the id of companyList table
		List clIds = uclReadDao.getCompanyListIds(userId, (page - 1) * 20);
		UserList userList = new UserList();

		List<CompanyListVO> companyListVOList = new ArrayList<CompanyListVO>();
		if (null != clIds && clIds.size() > 0) {
			for (int i = 0, size = clIds.size(); i < size; i++) {
				int clId = (Integer) clIds.get(i);
				CompanyListVO companyListVO = new CompanyListVO();
				// list 关联的companyId信息
				companyListVO.setCompanyList(clReadDao.get(clId));
				List<CompanyListRel> companyListRelList = clrReadDao.get(clId);
				companyListVO.setCompanyListRelList(companyListRelList);
				// 如果list下没有company，则total为零
				companyListVO.setCompanyCount(null == companyListRelList ? 0 : companyListRelList.size());
				companyListVOList.add(companyListVO);

			}
			userList.setCompanyListVOList(companyListVOList);
			userList.setListCount(companyListVOList.size());
		}
		return userList;
	}

	@Override
	public void updateDesc(int listId, String desc) {

		Timestamp time = new Timestamp(System.currentTimeMillis());
		CompanyList companyList = new CompanyList();
		companyList.setId(listId);
		companyList.setDescription(desc);
		companyList.setModifyTime(time);

		clWriteDao.updateDesc(companyList);
	}

	@Override
	public void deleteList(int listId) {

		Timestamp time = new Timestamp(System.currentTimeMillis());
		CompanyList companyList = new CompanyList();
		companyList.setId(listId);
		companyList.setActive('N');
		companyList.setModifyTime(time);

		clWriteDao.delete(companyList);
	}

	@Override
	public List getCompanyIds(int listId) {

		return clrReadDao.getCompanyIds(listId);
	}

	@Override
	public CompanyList getCompanyList(int listId) {

		return clReadDao.get(listId);
	}

	@Override
	public void createList(int userId, String name) {
		// 这里考虑名字重复的问题
		CompanyList cl = clReadDao.getByName(name);
		if (null != cl) {
			return;
		} else {
			Timestamp time = new Timestamp(System.currentTimeMillis());

			CompanyList companyList = new CompanyList();
			companyList.setName(name);
			companyList.setActive('Y');
			companyList.setCreateTime(time);
			companyList.setModifyTime(time);
			companyList.setStatus(ListStatus.PRIVATE.getValue());
			clWriteDao.insert(companyList);
			int companyListId = clReadDao.getIdByName(name);
			UserCompanyListRel uclr = new UserCompanyListRel();
			uclr.setUserId(userId);
			uclr.setCompanyListId(companyListId);
			uclr.setCreateTime(time);
			uclr.setModifyTime(time);
			uclr.setActive('Y');
			uclrWriteDao.insert(uclr);
		}
	}

	@Override
	public UserList getAllList(Integer userId) {
		// clIds is the id of companyList table
		List clIds = uclReadDao.getclIdsByUserId(userId);
		UserList userList = new UserList();

		List<CompanyListVO> companyListVOList = new ArrayList<CompanyListVO>();
		if (null != clIds && clIds.size() > 0) {
			for (int i = 0, size = clIds.size(); i < size; i++) {
				int clId = (Integer) clIds.get(i);
				CompanyListVO companyListVO = new CompanyListVO();
				// list 关联的companyId信息
				companyListVO.setCompanyList(clReadDao.get(clId));
				List<CompanyListRel> companyListRelList = clrReadDao.get(clId);
				companyListVO.setCompanyListRelList(companyListRelList);
				// 如果list下没有company，则total为零
				companyListVO.setCompanyCount(null == companyListRelList ? 0 : companyListRelList.size());
				companyListVOList.add(companyListVO);

			}
			userList.setCompanyListVOList(companyListVOList);
			userList.setListCount(companyListVOList.size());
		}
		return userList;
	}

	@Override
	public UserList getRelatedList(int userId, int companyId) {

		List<CompanyListVO> companyListVOList = new ArrayList<CompanyListVO>();
		List<CompanyListRel> clrList = clrReadDao.getByCompanyId(companyId);
		for (CompanyListRel clr : clrList) {
			int companyListId = clr.getCompanyListId();
			CompanyList cl = clReadDao.get(companyListId);
			CompanyListVO clVO = new CompanyListVO();
			clVO.setCompanyList(cl);
			companyListVOList.add(clVO);
		}
		UserList ul = new UserList();
		ul.setCompanyListVOList(companyListVOList);
		ul.setListCount(companyListVOList.size());
		return ul;
	}

}
