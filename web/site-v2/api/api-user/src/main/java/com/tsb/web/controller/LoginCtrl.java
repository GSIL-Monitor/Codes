package com.tsb.web.controller;

import java.util.HashMap;
import java.util.Map;

import javax.servlet.http.Cookie;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.user.UserEmailReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.dao.write.user.UserWriteDao;
import com.tsb.model.org.Organization;
import com.tsb.model.user.User;
import com.tsb.model.user.UserEmail;
import com.tsb.user.enums.LoginStatus;
import com.tsb.user.service.UserService;
import com.tsb.util.CookieManager;
import com.tsb.util.Email;
import com.tsb.util.RandomCodeFactory;


@Controller
@RequestMapping(value = "/api/user/login")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class LoginCtrl extends BaseController{

	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private UserEmailReadDao userEmailReadDao;
	
	@Autowired
	private UserWriteDao userWriteDao;

	@Autowired
	private OrganizationReadDao organizationReadDao;
	
	@Autowired
	private UserService userService;

	@Autowired
	@Qualifier("simpleMail")
	private Email simpleMail;
	
	@RequestMapping(value = "/verify", method=RequestMethod.POST)
	@ResponseBody
	public Map verify(HttpServletRequest request,
					HttpServletResponse response,
					@RequestBody String jsonRequest) {
		//System.out.println(jsonRequest);
		
		String email = null;
		String password = null;
		String ip = request.getHeader("X-Forwarded-For");
		if (ip == null || "".equals(ip.trim())) {
			ip = request.getHeader("X-Real-IP");
		}
		boolean isKeepLogin = false;
		//System.out.println("verify ip=" + ip);
		
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			Map<String, Object> payload = (Map<String, Object>)data.get("payload");
			email = (String)payload.get("email");
			//System.out.println("email=" + email);
			password = (String)payload.get("password");
			//System.out.println("password=" + password);
			isKeepLogin = (boolean)payload.get("autoLogin");
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		
		User beforeLoginUser = userReadDao.getByEmail(email);
		LoginStatus status= userService.login(email, password, ip, isKeepLogin);
		
		Map map = new HashMap();
		map.put("code", status.getValue());
		
		if(status == LoginStatus.SUCCESS) {
			User user = userReadDao.getByEmail(email);
			
			Cookie cookie = new Cookie("userid", "" + user.getId());
			cookie.setMaxAge(3600*24*360);
			cookie.setPath("/");
			response.addCookie(cookie);
			
			Cookie cookie1 = new Cookie("token", "" + user.getToken());
			cookie1.setHttpOnly(true);
			cookie1.setPath("/");
			response.addCookie(cookie1);
			
			if( isKeepLogin) {
				Cookie cookie2 = new Cookie("keeploginsecret", user.getKeepLoginSecret());
				cookie2.setMaxAge(3600*24*360);
				cookie2.setPath("/");
				response.addCookie(cookie2);
			}
			else {
				Cookie cookie2 = new Cookie("keeploginsecret", null);
				cookie2.setMaxAge(0);
				cookie2.setPath("/");
				response.addCookie(cookie2);
			}
			
			if( beforeLoginUser.getLastLoginTime() == null) {
				map.put("setting", true);
			}
			else{
				map.put("setting", false);
			}
			
			Organization org = organizationReadDao.getByUser(user.getId());
			map.put("grade", org.getGrade());
		}
		
		
		return map;
	}
	
	@RequestMapping(value = "/checkloginstatus", method=RequestMethod.POST)
	@ResponseBody
	public Map checkLoginStatus(HttpServletRequest request,
						HttpServletResponse response,
						@RequestBody String jsonRequest) {
		User user = null;
		String ip = request.getHeader("X-Forwarded-For");
		if (ip == null || "".equals(ip.trim())) {
			ip = request.getHeader("X-Real-IP");
		}
		//System.out.println("checkLoginStatus ip=" + ip);
		
		CookieManager cookieManager = new CookieManager(request, response);
		String strUserid = cookieManager.getCookieValue("userid");
		if( strUserid != null && !"".equals(strUserid) ){
        	int userid = 0;
        	try{
        		userid = Integer.parseInt(strUserid);
        	}
        	catch(Exception e){
        	}
        	if( userid > 0){
        		String token = cookieManager.getCookieValue("token");
        		if( token != null && !"".equals(token)){
        			User _user = userReadDao.getById(userid);
        			if( _user != null){
        				if(token.equals(_user.getToken())){
        					user = _user;
        				}
        			}
        		}
        		
        		if(user == null){
        			String keeploginsecret = cookieManager.getCookieValue("keeploginsecret");
        			LoginStatus status= userService.login(userid, keeploginsecret, ip);
        			if(status == LoginStatus.SUCCESS) {
        				user = userReadDao.getById(userid);
        				Cookie cookie = new Cookie("userid", "" + user.getId());
        				cookie.setMaxAge(3600*24*360);
        				cookie.setPath("/");
        				response.addCookie(cookie);
        				
        				Cookie cookie1 = new Cookie("token", "" + user.getToken());
        				cookie1.setHttpOnly(true);
        				cookie1.setPath("/");
        				response.addCookie(cookie1);
        			}
        		}
        	}
		}
				  
		Map map = new HashMap();
		map.put("code", 0);
		if( user == null) {
			map.put("login", false);
		}
		else{
			map.put("login", true);
			map.put("user", user);
			map.put("admin", userService.checkAdmin(user.getId()));
			map.put("organization", organizationReadDao.getByUser(user.getId()));
		}
		return map;
	}
	
	@RequestMapping(value = "/logout", method=RequestMethod.POST)
	@ResponseBody
	public Map logout(HttpServletRequest request,
						HttpServletResponse response,
						@RequestBody String jsonRequest) {
		CookieManager cookieManager = new CookieManager(request, response);
		String strUserid = cookieManager.getCookieValue("userid");
		if( strUserid != null && !"".equals(strUserid) ){
        	int userid = 0;
        	try{
        		userid = Integer.parseInt(strUserid);
        	}
        	catch(Exception e){
        	}
        	if( userid > 0){
        		String token = cookieManager.getCookieValue("token");
        		if( token != null && !"".equals(token)){
        			User user = userReadDao.getById(userid);
        			if( user != null){
        				user.setToken(null);
        				user.setKeepLoginSecret(null);
        				userWriteDao.update(user);
        			}
        		}
        	}
		}
				
		{
			Cookie cookie = new Cookie("userid", null);
			cookie.setMaxAge(0);
			cookie.setPath("/");
			response.addCookie(cookie);
		}
		{
			Cookie cookie = new Cookie("token", null);
			cookie.setMaxAge(0);
			cookie.setPath("/");
			response.addCookie(cookie);
		}
		{
			Cookie cookie = new Cookie("keeploginsecret", null);
			cookie.setMaxAge(0);
			cookie.setPath("/");
			response.addCookie(cookie);
		}
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/forgetpwd", method=RequestMethod.POST)
	@ResponseBody
	public Map forgetpwd(@RequestBody String jsonRequest) {
		//System.out.println(jsonRequest);
		Map map = new HashMap();
		
		String email = null;	
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			Map<String, Object> payload = (Map<String, Object>)data.get("payload");
			email = (String)payload.get("email");
			email = email.trim();
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		//System.out.println(email);
		
		if( email == null || "".equals(email)){
			map.put("code", -1);
			return map;
		}
		
		User user = userReadDao.getByEmail(email);
		if( user == null ){
			UserEmail ue = userEmailReadDao.getByEmail(email);
			if( ue != null && ue.getVerify() == true){
				user = userReadDao.getById(ue.getUserId());
			}
		}
		
		if( user == null ){
			map.put("code", -2);
			return map;
		}
		
		if( user.getOneTimePwd() == null || user.getOneTimePwd().length() != 16 ){
			user.setOneTimePwd(RandomCodeFactory.generateMixed(16).toLowerCase());
			userWriteDao.update(user);
		}

		Map templateVars = new HashMap();
		templateVars.put("user", user);
		simpleMail.sendMail("烯牛数据提醒：重新设置你的密码", email, "findpwd.ftl", templateVars);

		map.put("code", 0);
		return map;
	}
	
	@RequestMapping(value = "/resetpwd", method=RequestMethod.POST)
	@ResponseBody
	public Map resetpwd(@RequestBody String jsonRequest) {
		//System.out.println(jsonRequest);
		Map map = new HashMap();
		
		int userId = -1;
		String password = null;
		String oneTimePwd = null;
		try{
			ObjectMapper mapper = new ObjectMapper();
			Map<String, Object> data = (Map<String, Object>) mapper.readValue(jsonRequest, Map.class);
			Map<String, Object> payload = (Map<String, Object>)data.get("payload");
			userId = (Integer)payload.get("userId");
			password = (String)payload.get("password");
			oneTimePwd = (String)payload.get("oneTimePwd");
		}
		catch(Exception e) {
			e.printStackTrace();
		}
		if( userId <= 0 || password==null || oneTimePwd==null){
			map.put("code", -1);
			return map;
		}
		
		int code = userService.resetpwd(userId, oneTimePwd, password);
		
		map.put("code", code);
		return map;
	}
}
