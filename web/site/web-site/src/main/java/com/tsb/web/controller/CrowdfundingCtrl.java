package com.tsb.web.controller;

import java.io.IOException;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.model.crowdfunding.SourceCfMember;
import com.tsb.model.crowdfunding.SourceCrowdfunding;
import com.tsb.model.dict.CrowdfundingSource;
import com.tsb.model.dict.CrowdfundingStatus;
import com.tsb.model.vo.CfHeadVO;
import com.tsb.model.vo.CrowdfundingVO;
import com.tsb.service.CrowdfundingService;
import com.tsb.web.annotation.UserInfo;

@Controller
@RequestMapping(value = "/api/site/crowdfunding")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class CrowdfundingCtrl {
	@Autowired
	private CrowdfundingService crowdfundingService;

	@UserInfo(true)
	@RequestMapping(value = "/get")
	@ResponseBody
	public Map getCrowdById(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("id") Integer cfId) {

		CrowdfundingVO crowdfundingVO = crowdfundingService.getById(cfId);
		Map map = new HashMap();
		map.put("crowdfundingVO", crowdfundingVO);
		return map;
	}

	@UserInfo(true)
	@RequestMapping(value = "/getAll")
	@ResponseBody
	public Map getCrowdfundingByPage(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("page") int page, @RequestParam("status") String status,
			@RequestParam("source") String source) throws IOException {

		int st = 0;
		int sr = 0;

		for (CrowdfundingStatus cfStatus : CrowdfundingStatus.values()) {
			if (status.equals(cfStatus.getName())) {
				st = cfStatus.getValue();
			}
		}

		for (CrowdfundingSource cfSource : CrowdfundingSource.values()) {
			if (source.equals(cfSource.getName())) {
				sr = cfSource.getValue();
			}
		}

		// use sourceCrowdfunding because page need source and status
		List<SourceCrowdfunding> cfList = crowdfundingService.getByPage(page, st, sr);
		int total = crowdfundingService.count(st, sr);

		Map map = new HashMap();
		map.put("cfList", cfList);
		map.put("total", total);
		return map;
	}

	// @UserInfo(true)
	@RequestMapping(value = "/head")
	@ResponseBody
	public Map getHeadInfo(HttpServletRequest requset, HttpServletResponse response, @RequestParam("id") Integer id) {
		// id is cfId in source_crowdfunding
		CfHeadVO cfHeadVo = crowdfundingService.getCfHeadVOInfo(id);
		Map map = new HashMap();
		map.put("headInfo", cfHeadVo);
		return map;
	}

	// @UserInfo(true)
	@RequestMapping(value = "/member")
	@ResponseBody
	public Map getMemberByScfId(HttpServletRequest requset, HttpServletResponse response,
			@RequestParam("id") Integer id) {

		List<SourceCfMember> scfMemerList = crowdfundingService.getMembers(id);
		Map map = new HashMap();
		map.put("member", scfMemerList);
		return map;

	}
}
