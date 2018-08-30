package com.tsb.web.controller.user;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestMethod;
import org.springframework.web.bind.annotation.ResponseBody;

import com.tsb.company.service.UserDealService;
import com.tsb.company.vo.DealNoteVO;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/deal/note")
@SuppressWarnings(value = { "rawtypes", "unchecked" })
public class NoteCtrl extends BaseController {
	
	@Autowired
	private UserDealService userDealService;

	@RequestMapping(value = "/list", method = { RequestMethod.POST })
	@ResponseBody
	public Map getNoteList(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		String code = (String) request.getPayload().get("code");
		List<DealNoteVO> dealNoteVOList = userDealService.getDealNote(userId, code);
		Map map = new HashMap();
		map.put("notes", dealNoteVOList);
		map.put("code", 0);
		// 如果notes的userId和currentUserId不一样，直接在页面变成灰色，无法修改
		return map;
	}

	@RequestMapping(value = "/modify", method = { RequestMethod.POST })
	@ResponseBody
	public Map note(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		String code = (String) request.getPayload().get("code");
		String note = (String) request.getPayload().get("note");
		// 笔记id,null去新增，not null去update
		Integer noteId = (Integer) request.getPayload().get("noteId");

		userDealService.modifyDealNote(userId, code, noteId, note);
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}
	
	@RequestMapping(value = "/delete", method = { RequestMethod.POST })
	@ResponseBody
	public Map deleteNote(@RequestBody RequestVO request) {
		// 笔记id
		Integer noteId = (Integer) request.getPayload().get("noteId");
		userDealService.deleteDealNote(noteId);
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}
}
