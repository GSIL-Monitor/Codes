package com.tsb.web.interceptor;


import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.method.HandlerMethod;
import org.springframework.web.servlet.handler.HandlerInterceptorAdapter;

import com.tsb.service.UserService;
import com.tsb.user.model.User;
import com.tsb.web.annotation.UserInfo;
import com.tsb.web.util.CookieManager;



public class UserInfoInterceptor extends HandlerInterceptorAdapter {
	
	
	@Autowired
	private UserService userService;
	
	public boolean preHandle(HttpServletRequest request,
			HttpServletResponse response, Object handler) throws Exception {
//		if(!(handler instanceof HandlerMethod)) {
//			return true;
//		}
//		
//		HandlerMethod handlerMethod = (HandlerMethod) handler;
//		
//		UserInfo userInfo = handlerMethod.getBean().getClass().getAnnotation(UserInfo.class);
//		if( userInfo == null) {
//			userInfo = handlerMethod.getMethodAnnotation(UserInfo.class);
//		}
//		if(!userInfo.value()) return true;
//		
//		HttpSession session = request.getSession();
//		if(null == session.getAttribute("user")){
//			
//			CookieManager cookieManager = new CookieManager(request, response);
//	    	String username = cookieManager.getCookieValue("username");
//	    	if(username == null || username == ""){
//	    		response.getOutputStream().print("login");
////	    		response.sendRedirect("/"); 
//	    		return false;
//	    	}
//			
//	    	String autoLogin = cookieManager.getCookieValue("auto_login");
//	    	if(autoLogin == null || autoLogin == ""){
//	    		response.getOutputStream().print("login");
//	    		return false;
//	    	}
//	    	
//	    	User user = userService.getUserByUsername(username);
//			session.setAttribute("user", user);
//			
//			if( user == null ){
//				response.getOutputStream().print("login");
//				return false;
//			}
//		}
//      
		return true;
	}
	
}

