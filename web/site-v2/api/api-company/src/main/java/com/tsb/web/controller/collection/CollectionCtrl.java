package com.tsb.web.controller.collection;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.collection.CollectionService;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/collection")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class CollectionCtrl extends BaseController {
	@Autowired
	private CollectionService collectionService;

	// collection list
	@RequestMapping(value = "/list", method = { RequestMethod.POST })
	@ResponseBody
	public Map getCollections(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Map map = collectionService.getCollections(userId);
		map.put("code", 0);
		return map;

	}

	// 获取time_line company 总数
	@RequestMapping(value = "/count/timeLine", method = { RequestMethod.POST })
	@ResponseBody
	public Map countTimelineList(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Map map = new HashMap();
		map.put("total", collectionService.countTimeLie(userId));
		map.put("code", 0);
		return map;
	}

	// 获取time_line company list
	@RequestMapping(value = "/timeLineList", method = { RequestMethod.POST })
	@ResponseBody
	public Map getTimelineList(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		int start = (int) request.getPayload().get("start");
		int pageSize = (int) request.getPayload().get("pageSize");
		// map 种包含list，和time（最新时间）
		Map map = collectionService.getTimeLineComp(userId, start, pageSize);
		map.put("code", 0);

		return map;
	}

	// 获取collection company 总数
	@RequestMapping(value = "/count/collcomp", method = { RequestMethod.POST })
	@ResponseBody
	public Map countCollComps(@RequestBody RequestVO request) {
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		Map map = new HashMap();
		map.put("total", collectionService.countCollComp(collectionId));
		map.put("code", 0);
		return map;
	}

	// 每个collection下的company list
	@RequestMapping(value = "/compList", method = { RequestMethod.POST })
	@ResponseBody
	public Map getListByCollectionId(@RequestBody RequestVO request) {
		int userId = request.getUserid();
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int start = (int) request.getPayload().get("start");
		int pageSize = (int) request.getPayload().get("pageSize");
		Map map = collectionService.getCollCompList(collectionId, userId, start, pageSize);
		map.put("code", 0);
		return map;
	}

	// 移除collection
	@RequestMapping(value = "/remove/collection", method = { RequestMethod.POST })
	@ResponseBody
	public Map removeCollection(@RequestBody RequestVO request) {
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		collectionService.updateCollection(collectionId, userId, 'N');
		Map map = new HashMap();
		map.put("code", 0);

		return map;
	}

	// 激活系统近期热门collection
	@RequestMapping(value = "/active/collection", method = { RequestMethod.POST })
	@ResponseBody
	public Map activeCollection(@RequestBody RequestVO request) {
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		collectionService.updateCollection(collectionId, userId, 'Y');
		Map map = new HashMap();
		map.put("code", 0);

		return map;
	}

	// 筛选
	@RequestMapping(value = "/sort", method = { RequestMethod.POST })
	@ResponseBody
	public Map sortCompany(@RequestBody RequestVO request) {
		Integer sectorId = (Integer) request.getPayload().get("sector");
		Integer locationId = (Integer) request.getPayload().get("location");
		Integer round = (Integer) request.getPayload().get("location");
		// 如果collectionId 非空则是在具体collection中查询
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		int start = (int) request.getPayload().get("start");
		int pageSize = (int) request.getPayload().get("pageSize");
		Map map = collectionService.getSortCompList(userId, sectorId, locationId, round, collectionId, start, pageSize);
		map.put("code", 0);
		return map;
	}

	// 查询sort有多少记录
	@RequestMapping(value = "/sort/count", method = { RequestMethod.POST })
	@ResponseBody
	public Map countSortCompany(@RequestBody RequestVO request) {
		Integer sectorId = (Integer) request.getPayload().get("sector");
		Integer locationId = (Integer) request.getPayload().get("location");
		Integer round = (Integer) request.getPayload().get("location");
		// 如果collectionId 非空则是在具体collection中查询
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		Map map = new HashMap();
		map.put("total", collectionService.countSort(userId, sectorId, locationId, round, collectionId));
		map.put("code", 0);
		return map;
	}

	// @RequestMapping(value = "/update", method = { RequestMethod.POST })
	// @ResponseBody
	// public Map updateCollection(@RequestBody RequestVO request) {
	//
	// Map map = new HashMap();
	// map.put("code", 0);
	// return map;
	// }

	// 新增collection
	@RequestMapping(value = "/add", method = { RequestMethod.POST })
	@ResponseBody
	public Map addCollection(@RequestBody RequestVO request) {
		List<Integer> sectors = (List<Integer>) request.getPayload().get("sectors");
		List<Integer> locations = (List<Integer>) request.getPayload().get("locations");
		List<Integer> rounds = (List<Integer>) request.getPayload().get("rounds");
		List<Integer> investors = (List<Integer>) request.getPayload().get("investors");
		List<Integer> education = (List<Integer>) request.getPayload().get("educations");
		List<Integer> works = (List<Integer>) request.getPayload().get("works");
		// collection name
		String name = (String) request.getPayload().get("name");
		int userId = request.getUserid();
		collectionService.addCollection(sectors, locations, rounds, investors, education, works, name, userId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	// 更新
	@SuppressWarnings("unused")
	@RequestMapping(value = "/update", method = { RequestMethod.POST })
	@ResponseBody
	public Map updateCollection(@RequestBody RequestVO request) {
		List<Integer> sectors = (List<Integer>) request.getPayload().get("sectors");
		List<Integer> locations = (List<Integer>) request.getPayload().get("locations");
		List<Integer> rounds = (List<Integer>) request.getPayload().get("rounds");
		List<Integer> investors = (List<Integer>) request.getPayload().get("investors");
		List<Integer> education = (List<Integer>) request.getPayload().get("educations");
		List<Integer> works = (List<Integer>) request.getPayload().get("works");
		// collection name
		String name = (String) request.getPayload().get("name");
		Integer id = (Integer) request.getPayload().get("id");
		Map map = new HashMap();
		map.put("code", 0);
		return map;
	}

	// 关注某个collection
	@RequestMapping(value = "/follow", method = { RequestMethod.POST })
	@ResponseBody
	public Map followCollection(@RequestBody RequestVO request) {
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		collectionService.followCollection(collectionId, userId);
		Map map = new HashMap();
		map.put("code", 0);

		return map;
	}

	// 不再关注某个collection
	@RequestMapping(value = "/unfollow", method = { RequestMethod.POST })
	@ResponseBody
	public Map unFollowCollection(@RequestBody RequestVO request) {
		Integer collectionId = (Integer) request.getPayload().get("collectionId");
		int userId = request.getUserid();
		collectionService.unFollowCollection(collectionId, userId);
		Map map = new HashMap();
		map.put("code", 0);

		return map;
	}
}
