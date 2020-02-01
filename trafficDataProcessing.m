%%TODO: want to convert the data into a matric consisting of 
%%[time trafficCount1 trafficCount2 ...]

%for i in range 8 to 18, create logical array, extract traffic counts,
%transpose and append to the 8 to 18 column matrix.
data = [];
trafficCount = [];
figure;
for ii = 1:12
    j = ii+6;
    logical = j == hour1;
    matched_at_hour = all_motor_vehicles(logical);
    trafficCount(ii,:) = matched_at_hour';
    
end
hours = [7:18]';
trafficCountAvg = mean(trafficCount,2);
data = [hours trafficCountAvg];
plot(hours,trafficCountAvg,'k--','LineWidth',2)
%scatter(hour1,all_motor_vehicles)
hold on
for i = 5:7
    xdata = linspace(7,18,200);
    P = polyfit(hours,trafficCountAvg,i)
    %P = polyfit(hour1,all_motor_vehicles,i)
    fittedY = polyval(P,xdata);
    plot(xdata,fittedY)
    hold on
end
legend({'Data'  'Order 5' 'Order 6' 'Order 7'})

