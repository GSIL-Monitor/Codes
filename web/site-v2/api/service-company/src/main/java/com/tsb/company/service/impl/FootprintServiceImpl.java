package com.tsb.company.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.FootprintService;
import com.tsb.dao.read.company.FootprintReadDao;
import com.tsb.dao.write.company.FootprintWriteDao;
import com.tsb.model.company.CompanyTagRel;
import com.tsb.model.company.Footprint;

@Service
@SuppressWarnings("rawtypes")
public class FootprintServiceImpl implements FootprintService{

	@Autowired
	private FootprintReadDao footprintReadDao;
	
	@Autowired
	private FootprintWriteDao footprintWriteDao;
	
	@Override
	public List get(int companyId) {
		return footprintReadDao.getByCompanyId(companyId);
	}

	@Override
	public void addFootprints(List<Footprint> footprints, Integer userId) {
		for(Footprint foot: footprints){
			Timestamp time = new Timestamp(System.currentTimeMillis());	
			foot.setActive('Y');
			foot.setVerify('Y');
			foot.setCreateTime(time);
			foot.setCreateUser(userId);
			
			footprintWriteDao.insert(foot);
		}
	}
	
	
	@Override
	public void updateFootprints(List<Footprint> footprints, Integer userId) {
		for(Footprint foot: footprints){
			Timestamp time = new Timestamp(System.currentTimeMillis());	
			foot.setActive('Y');
			foot.setVerify('Y');
			foot.setModifyTime(time);
			foot.setModifyUser(userId);
			
			footprintWriteDao.update(foot);
		}
	}
	
	

	@Override
	public void deleteFootprints(List<Integer> ids, Integer userId) {
		for(Integer id: ids){
			footprintWriteDao.delete(id);
		}
	}


}
