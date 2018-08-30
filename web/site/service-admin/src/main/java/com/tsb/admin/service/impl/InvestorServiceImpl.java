package com.tsb.admin.service.impl;

import java.net.URL;
import java.sql.Timestamp;
import java.util.Date;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.google.common.net.InternetDomainName;
import com.tsb.admin.dao.read.InvestorReadDao;
import com.tsb.admin.dao.write.InvestorWriteDao;
import com.tsb.admin.service.InvestorService;
import com.tsb.model.Investor;

@Service
public class InvestorServiceImpl implements InvestorService {
	@Autowired
	private InvestorWriteDao investorWriteDao;
	
	@Autowired
	private InvestorReadDao investorReadDao;
	
	private void pre_process(Investor v){
		if(v.getWebsite() != null && v.getWebsite().trim() != ""){
			if( !v.getWebsite().toLowerCase().startsWith("http://") && !v.getWebsite().toLowerCase().startsWith("https://")){
				v.setWebsite("http://" + v.getWebsite());
			}
			try {
				URL url = new URL(v.getWebsite());
				String domain = InternetDomainName.from(url.getHost()).topPrivateDomain().toString();
				v.setDomain(domain);
			}
			catch(Exception e){
				e.printStackTrace();
			}
		}
	}
	
	@Override
	public void addInvestor(Investor v) {
		pre_process(v);
		
		v.setActive('Y');
		v.setVerify('Y');
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		v.setCreateTime(nousedate);
		v.setCreateUser(0);
		investorWriteDao.insert(v);
	}

	@Override
	public void updateInvestor(Investor v) {
		pre_process(v);
		
		v.setVerify('Y');
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		v.setModifyTime(nousedate);
		v.setModifyUser(0);
		investorWriteDao.update(v);
	}

	@Override
	public void deleteInvestor(Integer id) {
		Date date = new Date();       
		Timestamp nousedate = new Timestamp(date.getTime());
		
		Investor v = investorReadDao.getById(id);
		v.setActive('N');
		v.setModifyTime(nousedate);
		v.setModifyUser(0);
		investorWriteDao.update(v);
		
		//TODO funding_investor_rel investor_member
	}

}
