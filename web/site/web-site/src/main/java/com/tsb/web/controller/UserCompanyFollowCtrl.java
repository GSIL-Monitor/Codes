package com.tsb.web.controller;

import java.io.IOException;
import java.sql.Date;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;
import com.tsb.model.dict.FollowStatus;
import com.tsb.model.vo.FollowCompany;
import com.tsb.service.CompanyService;
import com.tsb.service.UserCompanyService;
import com.tsb.user.model.User;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value = "/api/site/user/company")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class UserCompanyFollowCtrl {

	@Autowired
	private UserCompanyService userCompanyService;
	@Autowired
	private CompanyService companyService;

	@UserInfo(true)
	@RequestMapping(value = "/getByStatus")
	@ResponseBody
	public Map getByStatus(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("status") String status) {

		User user = (User) requset.getSession().getAttribute("user");
		int statusValue = 0;
		for (FollowStatus fs : FollowStatus.values()) {
			if (fs.getName().equals(status))
				statusValue = fs.getValue();
		}
		List<FollowCompany> companyList = userCompanyService.getFolCompaniesByStatus(user.getId(), statusValue);
		Map map = new HashMap();
		map.put("companyList", companyList);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/unfollow", method = RequestMethod.DELETE)
	public void unfollow(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("companyCodes") String companyCodes) throws IOException {

		String[] codeArr = companyCodes.split(",");
		List companyCodeList = new ArrayList();
		for (String s : codeArr) {
			companyCodeList.add(s);
		}

		List companyIdList = companyService.getIdsByCompanyCodes(companyCodeList);

		User user = (User) requset.getSession().getAttribute("user");
		userCompanyService.unfollow(user.getId(), companyIdList);
	}

	@UserInfo(true)
	@RequestMapping(value = "/updateHeart", method = RequestMethod.PUT)
	public void updateHeart(HttpServletRequest requset, HttpServletResponse response, @RequestParam("code") String code,
			@RequestParam("heart") Character heart) throws IOException {

		int companyId = companyService.getIdByCode(code);
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();
		userCompanyService.updateHeart(userId, companyId, heart);
	}

	@UserInfo(true)
	@RequestMapping(value = "/updateFollow", method = RequestMethod.PUT)
	public void updateFollowing(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("code") String code, @RequestParam("status") int status, @RequestParam("start") String start)
					throws IOException {

		int companyId = companyService.getIdByCode(code);
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();
		String[] arr = start.split("/");

		Date ts = Date.valueOf(arr[2] + "-" + arr[0] + "-" + arr[1]);
		userCompanyService.updateFollowing(userId, companyId, status, ts);
	}

	@UserInfo(true)
	@RequestMapping(value = "/updateNote", method = RequestMethod.PUT)
	public void updateNote(HttpServletRequest requset, HttpServletResponse response, @RequestParam("code") String code,
			@RequestParam("note") String note) throws IOException {

		int companyId = companyService.getIdByCode(code);

		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();
		userCompanyService.updateNote(userId, companyId, note);
	}
}
