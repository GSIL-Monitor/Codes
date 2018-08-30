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

import com.tsb.api.NotifyOrganization;
import com.tsb.company.dao.DealScoreVODao;
import com.tsb.company.service.UserDealService;
import com.tsb.company.vo.DealScoreVO;
import com.tsb.company.vo.DealUserScoreVO;
import com.tsb.dao.read.company.CompanyReadDao;
import com.tsb.dao.read.org.DealReadDao;
import com.tsb.dao.read.org.OrganizationReadDao;
import com.tsb.dao.read.org.user.DealUserRelReadDao;
import com.tsb.dao.read.user.UserReadDao;
import com.tsb.model.org.Deal;
import com.tsb.model.org.Organization;
import com.tsb.model.org.user.DealUserRel;
import com.tsb.model.user.User;
import com.tsb.util.RequestVO;
import com.tsb.web.controller.BaseController;

@Controller
@RequestMapping(value = "/api/company/deal/score")
@SuppressWarnings({ "rawtypes", "unchecked" })
public class ScoreCtrl extends BaseController {
	@Autowired
	private CompanyReadDao companyReadDao;
	@Autowired
	private UserDealService userDealService;

	@Autowired
	private NotifyOrganization notify;
	
	@Autowired
	private UserReadDao userReadDao;
	
	@Autowired
	private OrganizationReadDao organizationReadDao;
	
	@Autowired
	private DealReadDao dealReadDao;
	
	@Autowired
	private DealUserRelReadDao dealUserRelReadDao;
	
	@Autowired
	private DealScoreVODao dealScoreVODao;
	
	@RequestMapping(value = "/get", method = { RequestMethod.POST })
	@ResponseBody
	public Map getUserScore(@RequestBody RequestVO request) {

		Integer userId = request.getUserid();
		String code = (String) request.getPayload().get("code");
		Integer companyId = companyReadDao.getIdByCode(code);
		List<DealUserScoreVO> dealUserScoreVOList = userDealService.getDealUserScore(userId, companyId);
		Map map = new HashMap();
		map.put("scores", dealUserScoreVOList);
		map.put("assignee", false);
		map.put("nextCode", "");
		map.put("code", 0);
		
		Organization org = organizationReadDao.getByUser(userId);
		Deal deal = dealReadDao.getByOrganization(companyId, org.getId());
		if( deal != null) {
			List<DealUserRel> list = dealUserRelReadDao.listByDealId(deal.getId());
			for(DealUserRel r : list){
				if( (r.getType() == 23020 || r.getType() == 23030) && r.getUserIdentify()==21020 
						&& r.getUserId() == userId ){
					map.put("assignee", true);
					DealScoreVO todo = dealScoreVODao.getNextScoring(org.getId(), userId, companyId);
					if( todo != null){
						map.put("nextCode", todo.getCompanyCode());
					}
				}
			}
		}
		return map;
	}

	@RequestMapping(value = "/modify", method = { RequestMethod.POST })
	@ResponseBody
	public Map score(@RequestBody RequestVO request) {
		Integer userId = request.getUserid();
		String code = (String) request.getPayload().get("code");
		int score = (int) request.getPayload().get("score");
		Integer type = Integer.parseInt((String)request.getPayload().get("type"));
		Integer companyId = companyReadDao.getIdByCode(code);
		
		userDealService.modifyDealScore(userId, companyId, score,type);
		
		User user = userReadDao.getById(userId);
		Organization org = organizationReadDao.getByUser(userId);
		Deal deal = dealReadDao.getByOrganization(companyId, org.getId());
		
		try{
			if(deal != null){
				notify.syncDeal(user,org,deal);
			}
		}
		catch(Exception e){
			e.printStackTrace();
		}
		
		Map map = new HashMap();
		map.put("code", 0);
		return map;

	}

}
