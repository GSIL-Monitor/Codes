package com.tsb.web.controller.user;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.enums.UserLogin;
import com.tsb.service.UserService;
import com.tsb.user.model.User;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value="/api/user")
@SuppressWarnings(value={"rawtypes","unchecked"})
public class UserCtrl {
	
	@Autowired
	private UserService userService;
	
	@UserInfo(false)
	@RequestMapping(value = "/check", method= RequestMethod.POST)
	@ResponseBody
	public Map checkUsername(HttpServletRequest requset,HttpServletResponse response,
					@RequestParam("param")String param,
					@RequestParam("type")Integer type){	
		
		boolean flag = userService.checkUser(param, type);
		
		Map map = new HashMap();
		map.put("result", flag);
		return map;
	}
	
	
	@UserInfo(false)
	@RequestMapping(value = "/register", method= RequestMethod.POST)
	@ResponseBody
	public Map register(HttpServletRequest requset,HttpServletResponse response,
					@RequestParam("username")String username,	
					@RequestParam("email")String email,
					@RequestParam("password")String password){
		
		userService.createUser(username, email, password);
		User user = userService.getUserSessionByUsername(username);
		requset.getSession().setAttribute("user", user);
		Map map = new HashMap();
		map.put("user", user);
		map.put("result", true);
		return map;
	}
	
}
