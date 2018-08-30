package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.CompanyService;
import com.tsb.company.service.MemberService;
import com.tsb.company.vo.MemberVO;
import com.tsb.util.RequestVO;

@Controller
@RequestMapping(value = "/api/company/member")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class MemberCtrl extends BaseController{
	@Autowired
	private MemberService memberService;

	@RequestMapping(value = "/list",method=RequestMethod.POST)
	@ResponseBody
	public Map getMembers(@RequestBody RequestVO request){
		int id= (int) request.getPayload().get("id");
		List<MemberVO> memberVOList= memberService.getMembers(id);
		Map map =new HashMap();
		map.put("members", memberVOList);
		map.put("code", 0);
		return map;
		
	}

	
}
