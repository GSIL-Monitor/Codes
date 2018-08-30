package com.tsb.service.impl;

import java.sql.Timestamp;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.model.user.CompanyList;
import com.tsb.model.user.CompanyListRel;
import com.tsb.service.CompanyListService;
import com.tsb.user.dao.read.CompanyListRelReadDao;
import com.tsb.user.dao.write.CompanyListRelWriteDao;
import com.tsb.user.dao.write.CompanyListWriteDao;

@Service
public class CompanyListServiceImpl implements CompanyListService{
	@Autowired
	private CompanyListRelReadDao clrReadDao;
	
	@Autowired
	private CompanyListRelWriteDao clrWriteDao;
	@Autowired
	private CompanyListWriteDao clWriteDao;
	@SuppressWarnings("rawtypes")
	@Override
	public void createCompanyListRel(List listIdList, List companyIdList) {
		//但凡有增删改都操作都要纪录时间
		Timestamp time = new Timestamp(System.currentTimeMillis());
		//check exiting
		for(int i=0,listIdSize=listIdList.size();i<listIdSize;i++){
			int companyListId=(Integer) listIdList.get(i);
			for(int j=0,cIdSize=companyIdList.size();j<cIdSize;j++){
				
				
				int companyId=(Integer) companyIdList.get(j);
				//if not exiting, companyListRel==null
				CompanyListRel  companyListRel = clrReadDao.getCompanyListRel(companyListId,companyId);
				
				if(null==companyListRel){
					CompanyListRel clr = new CompanyListRel();
					clr.setActive('Y');
					clr.setCreateTime(time);
					clr.setCompanyId(companyId);
					clr.setCompanyListId(companyListId);
					
					clrWriteDao.insert(clr);
				}
				else{
					companyListRel.setModifyTime(time);
					clrWriteDao.updateModifyTime(companyListRel);
				}
			}
			CompanyList cl = new CompanyList();
			cl.setId(companyListId);
			cl.setModifyTime(time);
			clWriteDao.updateModifyTime(cl);
		}
		
	}

}
