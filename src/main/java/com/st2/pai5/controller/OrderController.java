package com.st2.pai5.controller;

import com.st2.pai5.model.HotelOrder;
import com.st2.pai5.model.OrderDTO;
import com.st2.pai5.service.OrderService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/order")
public class OrderController {

    private final OrderService orderService;

    @Autowired
    public OrderController(OrderService orderService) {
        this.orderService = orderService;
    }

    @PostMapping("")
    public ResponseEntity<Object> postOrder(@RequestBody OrderDTO order) {
        return ResponseEntity.accepted().build();
    }

}
