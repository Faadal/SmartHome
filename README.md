# IoT-Smart-Home

## Introduction

This repository aims at gathering an academic project I developed for Saint-Gobain Research, which consisted in the development of an autonomous predictive platform. As this project is partly confidential, I am only able to present the code making the platform autonomous. The whole strategy is based on parsers, mastered APIs, web scrapping, logs, e-mails and DataFrames.

## Structure

On the whole, the project follows a simple hierarchical structure :

* APIs given raw data through requests (AirQuality, Weather, Sensor Measures, ...) ;
* Parsers extracting that raw data, while correcting it ;
* Correction is applied for missing values on the whole database ;
* Camera snapshots are made for vision ;
* Scrapping of the school agenda for the amount of students per classes ;

## Aim

The aim of such project is, as presented, a predictive platform able to quantify and quality the air quality of every room in the school, as it may get oriented towards smart consumption and comfort.