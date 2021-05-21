package com.st2.pai5.model;

import lombok.Getter;
import lombok.Setter;

import javax.persistence.Column;
import javax.persistence.Entity;
import javax.persistence.GeneratedValue;
import javax.persistence.Id;

@Entity
@Getter
@Setter
public class HotelOrder {
    @Id
    @GeneratedValue
    private Integer id;

    @Column(name = "beds")
    private Integer beds;

    @Column(name = "tables")
    private Integer tables;

    @Column(name = "chairs")
    private Integer chairs;

    @Column(name = "armchairs")
    private Integer armchairs;


}
