package com.st2.pai5.repository;

import com.st2.pai5.model.HotelOrder;
import org.springframework.data.jpa.repository.JpaRepository;

public interface OrderRepository extends JpaRepository<HotelOrder, Integer> {
}
