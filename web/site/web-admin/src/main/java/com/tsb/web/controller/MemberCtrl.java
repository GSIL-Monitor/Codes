package com.tsb.web.controller;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.admin.dao.read.MemberReadDao;
import com.tsb.admin.dao.read.source.SourceMemberReadDao;
import com.tsb.admin.service.MemberService;
import com.tsb.admin.vo.MemberVO;
import com.tsb.admin.vo.SourceMemberVO;
import com.tsb.model.CompanyMemberRel;
import com.tsb.model.Member;
import com.tsb.model.source.SourceMember;

@Controller
@RequestMapping(value = "/api/admin/member")
public class MemberCtrl {

	@Autowired
	private MemberService memberService;
	@Autowired
	private MemberReadDao memberReadDao;
	@Autowired
	private SourceMemberReadDao sourceMemberReadDao;
	
	@RequestMapping(value = "/get")
	@ResponseBody
	public Member getMember(@RequestParam("id") Integer id) {
		Member m = memberReadDao.get(id);
		if(m == null){
			return null;
		}
		if(m.getActive() == 'N'){
			return null;
		}
		return m;
	}
	
	@RequestMapping(value = "/source/list")
	@ResponseBody
	public List<SourceMember> listSourceMembers(@RequestParam("id") Integer id) {
		return sourceMemberReadDao.listByMemberId(id);
	}
	
	@RequestMapping(value = "/get/all")
	@ResponseBody
	public List<MemberVO> listMemberVOsByCompanyId(@RequestParam("id") Integer companyId) {
		return memberService.listMemberVOsByCompanyId(companyId);
	}
	
	@RequestMapping(value = "/source/get/all")
	@ResponseBody
	public List<SourceMemberVO> listSourceMemberVOsByCompanyMemberRelId(@RequestParam("id") Integer sourceCompanyMemberRelId) {
		return memberService.listSourceMemberVOsByCompanyMemberRelId(sourceCompanyMemberRelId);
	}
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/updatemember", method={RequestMethod.PUT})
	@ResponseBody
	public Map updateMember(@RequestBody Member member) {
		memberService.updateMember(member);
		HashMap map = new HashMap();
		map.put("code", 0);
		map.put("member", member);
		return map;
	}
	
	@RequestMapping(value = "/deletemember", method={RequestMethod.PUT})
	@ResponseBody
	public String deletemember(@RequestBody Member m) {
		memberService.deleteMember(m.getId());
		return "{'code':0}";
	}
	
	@RequestMapping(value = "/update", method={RequestMethod.PUT})
	@ResponseBody
	public String updateMemberAndRel(@RequestBody MemberVO memberVO) {
		memberService.updateMemberAndRel(memberVO);
		return "{'code':0}";
	}
	
	@RequestMapping(value = "/delete", method={RequestMethod.PUT})
	@ResponseBody
	public String deleteCompanyMemberRel(@RequestBody CompanyMemberRel r) {
		memberService.deleteCompanyMemberRel(r);
		return "{'code':0}";
	}
	
	@SuppressWarnings({ "rawtypes", "unchecked" })
	@RequestMapping(value = "/add", method={RequestMethod.PUT})
	@ResponseBody
	public Map addMember(@RequestBody Member m) {
		memberService.addMember(m);
		HashMap map = new HashMap();
		map.put("code", 0);
		map.put("member", m);
		return map;
	}
}
