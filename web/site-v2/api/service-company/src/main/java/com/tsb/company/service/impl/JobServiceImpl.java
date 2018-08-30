package com.tsb.company.service.impl;

import java.util.ArrayList;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import com.tsb.company.service.JobService;
import com.tsb.company.vo.JobVO;
import com.tsb.dao.read.LocationReadDao;
import com.tsb.dao.read.company.JobReadDao;
import com.tsb.model.company.Job;

@Service
@SuppressWarnings({"rawtypes", "unchecked"})
public class JobServiceImpl implements JobService{

	@Autowired
	private JobReadDao jobReadDao;
	
	@Autowired
	private LocationReadDao locationReadDao;
	
	@Override
	public List getJobs(int companyId) {
		List<Job> list =  jobReadDao.getByCompanyId(companyId);
		List jobVOs = new ArrayList();
		for(Job job : list){
			JobVO jobVO = new JobVO();
			jobVO.setJob(job);
			if(job.getLocationId() > 0)
				jobVO.setLocation(locationReadDao.get(job.getLocationId()));
			
			jobVOs.add(jobVO);
		}

		return jobVOs;
	}

}
