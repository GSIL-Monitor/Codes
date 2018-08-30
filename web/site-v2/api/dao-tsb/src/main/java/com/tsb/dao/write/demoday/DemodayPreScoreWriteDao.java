package com.tsb.dao.write.demoday;

import com.tsb.model.demoday.DemodayPreScore;

public interface DemodayPreScoreWriteDao {
	void insert(DemodayPreScore demodayPrescore);

	void update(DemodayPreScore demodayPrescore);
	
	void delete(Integer dealDemodayId);
}
