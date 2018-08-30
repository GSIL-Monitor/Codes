package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.apache.ibatis.annotations.Param;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.model.user.CompanyList;
import com.tsb.model.vo.CompanyVO;
import com.tsb.service.CompanyService;
import com.tsb.service.UserListService;
import com.tsb.user.model.User;
import com.tsb.user.model.vo.UserList;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value = "/api/site/user/list")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class UserListCtrl {
	@Autowired
	private UserListService userListService;
	@Autowired
	private CompanyService companyService;

	@UserInfo(true)
	@RequestMapping(value = "/get")
	@ResponseBody
	public Map getUserList(HttpServletRequest request, HttpServletResponse response, @Param("page") int page) {
		User user = (User) request.getSession().getAttribute("user");
		int userId = user.getId();
		UserList userList = userListService.getUserList(userId, page);
		userList.setUserId(userId);
		Map map = new HashMap();
		map.put("userList", userList);
		return map;

	}

	@UserInfo(true)
	@RequestMapping(value = "/updateDesc", method = RequestMethod.PUT)
	public void updateDesc(HttpServletRequest requset, HttpServletResponse response, @RequestParam("id") int listId,
			@RequestParam("desc") String desc) {
		userListService.updateDesc(listId, desc);
	}

	@UserInfo(true)
	@RequestMapping(value = "/deleteOwner", method = RequestMethod.DELETE)
	public void delete(HttpServletRequest requset, HttpServletResponse response, @RequestParam("id") int listId) {
		userListService.deleteList(listId);
	}

	@UserInfo(true)
	@RequestMapping(value = "/overview")
	@ResponseBody
	public Map overview(HttpServletRequest requset, HttpServletResponse response, @RequestParam("id") int id) {
		// 根据listId 获取company id
		CompanyList listInfo = userListService.getCompanyList(id);
		List companyIds = userListService.getCompanyIds(id);
		List<CompanyVO> companyVOs = companyService.getCompanies(companyIds);
		Map map = new HashMap();
		map.put("listInfo", listInfo);
		map.put("companyList", companyVOs);
		return map;

	}

	@UserInfo(true)
	@RequestMapping(value = "/create", method = RequestMethod.PUT)
	public void create(HttpServletRequest requset, HttpServletResponse response, @RequestParam("name") String name) {
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();

		userListService.createList(userId, name);
	}

	@UserInfo(true)
	@RequestMapping(value = "/getAll")
	@ResponseBody
	public Map getAllList(HttpServletRequest requset, HttpServletResponse response) {
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();

		UserList userList = userListService.getAllList(userId);

		Map map = new HashMap();
		map.put("userList", userList);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/search")
	public void search(HttpServletRequest requset, HttpServletResponse response) {

		return;
	}

	@UserInfo(true)
	@RequestMapping(value = "/getExsiting")
	@ResponseBody
	public Map getExsitingList(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("code") String code) {
		int companyId = companyService.getIdByCode(code);
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();

		UserList exsitingList = userListService.getRelatedList(userId, companyId);
		Map map = new HashMap();
		map.put("exsitingList", exsitingList);
		return map;
	}
}