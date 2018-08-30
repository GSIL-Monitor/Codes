package com.tsb.admin.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.admin.service.UserService;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.read.user.UserRoleReadDao;
import com.tsb.dao.write.org.UserOrganizationRelWriteDao;
import com.tsb.dao.write.user.UserRoleWriteDao;
import com.tsb.dao.write.user.UserWriteDao;
import com.tsb.model.org.UserOrganizationRel;
import com.tsb.model.user.User;
import com.tsb.model.user.UserRole;
import com.tsb.util.MD5;

@Service
@SuppressWarnings("rawtypes")
public class UserServiceImpl implements UserService {
	private final String SALT = "24114581331805856724";
	@Autowired
	private UserOrganizationRelWriteDao userOrgRelWriteDao;
	@Autowired
	private UserWriteDao userWriteDao;
	@Autowired
	private UserReadDao userReadDao;
	@Autowired
	private UserRoleWriteDao userRoleWriteDao;
	@Autowired
	private UserRoleReadDao userRoleReadDao;

	@Override
	public void addUser(Integer orgId, User user, List<Integer> roles) {
		Timestamp time = new Timestamp(System.currentTimeMillis());

		user.setCreateTime(time);
		user.setActive('Y');
		userWriteDao.insert(user);

		Integer userId = user.getId();
		MD5 md5 = new MD5();
		String str = SALT + userId.intValue() + user.getPassword();
		String md5Pwd = md5.getMD5ofUTF8Str(str);
		user.setPassword(md5Pwd);
		userWriteDao.update(user);

		if (roles != null && !roles.isEmpty()) {
			for (Integer role : roles) {
				UserRole userRole = new UserRole();
				userRole.setCreateTime(time);
				userRole.setUserId(userId);
				userRole.setRole(role);

				userRoleWriteDao.insert(userRole);
			}
		}

		UserOrganizationRel userOrgRel = new UserOrganizationRel();
		userOrgRel.setOrganizationId(orgId);
		userOrgRel.setUserId(user.getId());
		userOrgRel.setCreateTime(time);
		userOrgRelWriteDao.insert(userOrgRel);

	}

	@Override
	public void deleteUser(Integer userId, Integer orgId) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		User user = userReadDao.getById(userId);
		user.setActive('N');
		user.setModifyTime(time);
		userWriteDao.update(user);
	}

	@Override
	public void update(User user, List roles) {
		Timestamp time = new Timestamp(System.currentTimeMillis());
		Integer userId = user.getId();
		User old = userReadDao.getById(userId);
		old.setUsername(user.getUsername());
		old.setEmail(user.getEmail());
		old.setModifyTime(time);
		userWriteDao.update(old);
		update(roles, userId);

	}

	protected void update(List roles, int userId) {
		List<UserRole> userRoles = userRoleReadDao.getUserRoles(userId);
		Timestamp time = new Timestamp(System.currentTimeMillis());
		int size = roles.size();
		// userRoles 为空
		boolean userRolesFlage = (null == userRoles || userRoles.isEmpty());
		// 传入的roles为空
		boolean rolesFlage = (null == roles || roles.isEmpty());
		// 二者都为空，不做操作
		if (userRolesFlage && rolesFlage) {
			return;
		}
		// userRoles 空，roles不为空,新增所有roles
		else if (userRolesFlage && !rolesFlage) {
			for (int i = 0; i < size; i++) {
				UserRole newUserRole = new UserRole();
				newUserRole.setUserId(userId);
				Integer role = (Integer) roles.get(i);
				newUserRole.setRole(role);
				newUserRole.setCreateTime(time);
				userRoleWriteDao.insert(newUserRole);
			}
			return;
		}
		// userRoles 不为空，传入空roles，删除所有role
		else if (!userRolesFlage && rolesFlage) {
			for (UserRole userRole : userRoles) {
				userRoleWriteDao.delete(userRole.getId());
			}
			return;
		}

		// 下面是二者都不为空
		// 标记该role是否被删除
		boolean remove = true;
		for (UserRole userRole : userRoles) {
			int role = userRole.getRole();
			remove = true;
			for (int i = 0; i < size; i++) {
				// 在新的role列表中找到了该role，保留
				if ((Integer) roles.get(i) == role) {
					remove = false;
					break;
				}
			}
			// 在新的role列表中没有该role，删除
			if (remove)
				userRoleWriteDao.delete(userRole.getId());
		}

		boolean add = true;
		for (int i = 0; i < size; i++) {
			int roleType = (Integer) roles.get(i);
			add = true;
			for (UserRole userRole : userRoles) {
				// 在旧的列表中找到该role，不新增
				if (roleType == userRole.getRole()) {
					add = false;
					break;
				}
			}
			if (add) {
				UserRole newUserRole = new UserRole();
				newUserRole.setUserId(userId);
				newUserRole.setRole(roleType);
				newUserRole.setCreateTime(time);
				userRoleWriteDao.insert(newUserRole);
			}
		}

	}

	@Override
	public boolean getUser(String email) {
		return null != userReadDao.getByEmail(email);
	}

}
