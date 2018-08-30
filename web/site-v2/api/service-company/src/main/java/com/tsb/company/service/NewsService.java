package com.tsb.company.service;

import java.util.List;

import com.tsb.company.vo.NewsVO;

public interface NewsService {
	List get(int companyId);
	NewsVO getVO(int companyId, int newsId);
}
