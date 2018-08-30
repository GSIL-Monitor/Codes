package com.tsb.web.controller;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeSet;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.model.Artifact;
import com.tsb.model.Member;
import com.tsb.model.dict.ArtifactType;
import com.tsb.model.user.UserCompanyFollow;
import com.tsb.model.user.UserCompanyNote;
import com.tsb.model.vo.CompanyHeadVO;
import com.tsb.model.vo.CompanyMemberRelVO;
import com.tsb.model.vo.CompanyVO;
import com.tsb.model.vo.MemberExperience;
import com.tsb.service.CompanyService;
import com.tsb.service.UserCompanyService;
import com.tsb.user.model.User;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value = "/api/site/company")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class CompanyCtrl {

	@Autowired
	private CompanyService companyService;
	@Autowired
	private UserCompanyService userCompanyService;

	@UserInfo(true)
	@RequestMapping(value = "/overview")
	@ResponseBody
	public Map getCompanyByCode(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("code") String code) {
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();

		int companyId = companyService.getIdByCode(code);

		CompanyVO company = companyService.getByCode(code);

		UserCompanyFollow ucf = userCompanyService.getByUserIdAndCompanyId(userId, companyId);
		UserCompanyNote ucn = userCompanyService.getUserCompanyNote(userId, companyId);
		company.setUserCompanyFollow(ucf);
		company.setUserCompanyNote(ucn);
		List atTypes = new ArrayList<Integer>();
		for (Artifact artifact : company.getArtifactList()) {
			atTypes.add(artifact.getType());
		}
		TreeSet<Integer> artifactTypes = new TreeSet<Integer>(atTypes);
		Map map = new HashMap();
		map.put("company", company);
		map.put("artifactType", artifactTypes);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/getCompanies", method = RequestMethod.POST)
	@ResponseBody
	public Map getCompaniesByCodes(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("codes") String codes) {
		String[] codeArr = codes.split(",");
		List<String> codeLlist = new ArrayList<String>();
		for (String s : codeArr) {
			codeLlist.add(s);
		}
		List compIdList = companyService.getIdsByCompanyCodes(codeLlist);

		List<CompanyVO> resultList = companyService.getCompanies(compIdList);

		Map map = new HashMap();
		map.put("companyList", resultList);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/team")
	@ResponseBody
	public Map getTeam(HttpServletRequest requset, HttpServletResponse response, @RequestParam("code") String code) {
		int companyId = companyService.getIdByCode(code);

		List<CompanyMemberRelVO> cmrVOList = companyService.getMembers(companyId);

		// List<CompanyMemberRelVO> teamList = new
		// ArrayList<CompanyMemberRelVO>();
		// for (CompanyMemberRelVO mem : cmrVOList) {
		// String work = mem.getMember().getWorkExperience();
		// work = work.replaceAll("<p class='p-underline'>",
		// "").replaceAll("<p>", "").replaceAll("</p>", "");
		// mem.getMember().setWorkExperience(work);
		// teamList.add(mem);
		// }

		// List<CompanyJob> jobs = companyService.getJobs(companyId);
		// List<CompanyRecruitSummary> recruitSummary =
		// companyService.getRecuritSummary(companyId);

		Map map = new HashMap();
		map.put("team", cmrVOList);
		// map.put("team", teamList);
		// map.put("jobs", jobs);
		// map.put("recruit", recruitSummary);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/head")
	@ResponseBody
	public Map getHeadInfo(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("code") String code) {
		int companyId = companyService.getIdByCode(code);
		User user = (User) requset.getSession().getAttribute("user");
		int userId = user.getId();

		CompanyHeadVO vo = companyService.getHeadInfo(userId, companyId);
		vo.setUserCompanyFollow(userCompanyService.getByUserIdAndCompanyId(userId, companyId));
		Map map = new HashMap();
		map.put("headInfo", vo);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/member")
	@ResponseBody
	public Map getMemberInfo(HttpServletRequest request, HttpServletResponse response, @RequestParam("id") int id) {

		Member member = companyService.getMember(id);
		List<MemberExperience> meList = companyService.getMemberExperienc(id);
		Map map = new HashMap();
		map.put("member", member);
		map.put("experience", meList);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/artifact")
	@ResponseBody
	public Map getArtifactByType(HttpServletRequest request, HttpServletResponse response, @RequestParam("id") int id,
			@RequestParam("type") String type) {

		int atType = 0;
		for (ArtifactType artifactType : ArtifactType.values()) {
			if (type.equals(artifactType.getName())) {
				atType = artifactType.getValue();
			}
		}
		List<Artifact> atList = companyService.getArtifacts(id, atType);
		Map map = new HashMap();
		map.put("artifact", atList);
		return map;

	}

	@UserInfo(true)
	@RequestMapping(value = "/verify", method = RequestMethod.PUT)
	public void verifyCompany(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("code") String code, @RequestParam("verify") Character verify) {
		int companyId = companyService.getIdByCode(code);
		companyService.verify(companyId, verify);

	}
}
