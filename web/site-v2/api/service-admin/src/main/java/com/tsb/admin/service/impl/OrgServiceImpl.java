package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.dao.UsersInfoReadDao;
import com.tsb.admin.service.OrgService;
import com.tsb.admin.vo.UsersInfoVO;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.org.UserOrganizationRelReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.read.user.UserRoleReadDao;
import com.tsb.dao.write.demoday.DemodayOrganizationWriteDao;
import com.tsb.dao.write.org.OrganizationWriteDao;
import com.tsb.dao.write.org.UserOrganizationRelWriteDao;
import com.tsb.dao.write.user.UserWriteDao;
import com.tsb.model.org.Organization;
import com.tsb.model.user.User;

@Service
@SuppressWarnings({ "rawtypes", "unchecked" })
public class OrgServiceImpl implements OrgService {
	@Autowired
	private OrganizationReadDao orgReadDao;
	@Autowired
	private OrganizationWriteDao orgWriteDao;
	@Autowired
	private UserOrganizationRelReadDao userOrgRelReadDao;
	@Autowired
	private UserOrganizationRelWriteDao userOrgRelWriteDao;
	@Autowired
	private UserWriteDao userWriteDao;
	@Autowired
	private UserReadDao userReadDao;
	@Autowired
	private DemodayOrganizationWriteDao demodayOrgWriteDao;
	@Autowired
	private UsersInfoReadDao usersInfoReadDao;
	@Autowired
	private UserRoleReadDao userRoleReadDao;

	@Override
	public List getOrgs() {
		return orgReadDao.getOrgs();
	}

	@Override
	public Organization getOrg(String name) {

		return orgReadDao.getOrgByName(name);
	}

	@Override
	public void addOrg(Organization org) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		org.setCreateTime(time);
		orgWriteDao.insert(org);

	}

	@Override
	public void deleteOrg(Integer id) {
		List<Integer> userIds = userOrgRelReadDao.getUserIds(id);
		Timestamp time = new Timestamp(System.currentTimeMillis());
		for (Integer userId : userIds) {
			User user = userReadDao.getById(userId);
			user.setActive('N');
			user.setModifyTime(time);
			userWriteDao.update(user);
		}
		demodayOrgWriteDao.delete(id);
		userOrgRelWriteDao.delete(id);
		orgWriteDao.delete(id);

	}

	@Override
	public void update(Organization org) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		org.setModifyTime(time);
		orgWriteDao.update(org);

	}

	@Override
	public Map getOrgUsersInfo(int id, int from, int pageSize) {
		Map map = new HashMap();
		List<UsersInfoVO> userList = usersInfoReadDao.get(id, from, pageSize);
		if (null != userList && !userList.isEmpty()) {
			for (UsersInfoVO user : userList) {
				user.setRoles(userRoleReadDao.getRoles(user.getUserId()));
			}
		}
		map.put("list", userList);
		return map;
	}

	@Override
	public Map coutOrgUsersInfo(int id) {
		Map map = new HashMap();
		map.put("orgName", orgReadDao.get(id).getName());
		map.put("totalUser", usersInfoReadDao.getUsersNum(id));
		return map;
	}

	@Override
	public Map getOrgUsersInfo(int id) {
		Map map = new HashMap();
		List<UsersInfoVO> userList = usersInfoReadDao.getById(id);
		if (null != userList && !userList.isEmpty()) {
			for (UsersInfoVO user : userList) {
				user.setRoles(userRoleReadDao.getRoles(user.getUserId()));
			}
		}
		map.put("list", userList);
		return map;
	}

}
