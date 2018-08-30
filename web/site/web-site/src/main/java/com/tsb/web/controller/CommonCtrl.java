package com.tsb.web.controller;

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.model.dict.CrowdfundingSource;
import com.tsb.model.dict.CrowdfundingStatus;
import com.tsb.model.dict.FollowStatus;
import com.tsb.model.dict.FundingRound;
import com.tsb.model.dict.SearchBy;

@Controller
@RequestMapping(value = "/api/site/common")
@SuppressWarnings({ "unchecked", "rawtypes" })
public class CommonCtrl {
	// @UserInfo(true)
	@RequestMapping(value = "/followStatus")
	@ResponseBody
	public Map<String, Object> FollowStatus() {
		List followStatusList = new ArrayList();
		for (FollowStatus fs : FollowStatus.values()) {
			Map<String, String> map = new HashMap<String, String>();
			map.put("text", fs.getName());
			map.put("id", fs.getValue() + "");
			followStatusList.add(map);
		}

		Map map = new HashMap();
		map.put("followStatus", followStatusList);
		return map;
	}

	// @UserInfo(true)
	@RequestMapping(value = "/crowdfundingStatus")
	@ResponseBody
	public Map cfStatus() throws IOException {
		List cfStatuslist = new ArrayList();
		for (CrowdfundingStatus cfStatus : CrowdfundingStatus.values()) {
			Map<String, String> map = new HashMap<String, String>();
			map.put("name", cfStatus.getName());
			map.put("value", cfStatus.getValue() + "");
			cfStatuslist.add(map);
		}

		Map map = new HashMap();
		map.put("list", cfStatuslist);
		return map;
	}

	// @UserInfo(true)
	@RequestMapping(value = "/crowdfundingSource")
	@ResponseBody
	public Map cfSource() throws IOException {
		List list = new ArrayList();
		for (CrowdfundingSource cfSource : CrowdfundingSource.values()) {
			Map<String, String> map = new HashMap<String, String>();
			map.put("name", cfSource.getName());
			map.put("value", cfSource.getValue() + "");
			list.add(map);
		}

		Map map = new HashMap();
		map.put("list", list);
		return map;
	}

	// @UserInfo(true)
	@RequestMapping(value = "/searchBy")
	@ResponseBody
	public Map<String, Object> searchBy() {
		List searchBylist = new ArrayList();
		for (SearchBy searchBy : SearchBy.values()) {
			Map<String, String> map = new HashMap<String, String>();
			map.put("name", searchBy.getName());
			map.put("value", searchBy.getValue() + "");
			searchBylist.add(map);
		}

		List fundingRoundList = new ArrayList();
		for (FundingRound round : FundingRound.values()) {
			Map<String, String> map = new HashMap<String, String>();
			map.put("name", round.getName());
			map.put("value", round.getValue() + "");
			fundingRoundList.add(map);
		}

		Map map = new HashMap();
		map.put("searchBy", searchBylist);
		map.put("fundingRound", fundingRoundList);
		return map;
	}

}
