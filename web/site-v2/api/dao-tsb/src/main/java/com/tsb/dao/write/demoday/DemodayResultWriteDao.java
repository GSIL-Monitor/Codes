package com.tsb.dao.write.demoday;

import com.tsb.model.demoday.DemodayResult;

public interface DemodayResultWriteDao {
	void insert(DemodayResult demodayResult);

	void update(DemodayResult demodayResult);
	
	void delete(Integer demodayCompanyId);
}
