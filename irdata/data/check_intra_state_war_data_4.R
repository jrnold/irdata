#!/usr/bin/env Sweave
## Check that initiator is either in SideA or SideB
library(foreign)
fname <- "IntraStateWarData_v4.1.csv"

wars <- read.csv(fname, stringsAsFactors = FALSE)

cat("Checking that Initiator values are in SideA or SideB\n")

for (x in split(wars, wars$WarNum)) {
    partic <- unique(c(x$SideA, x$SideB))
    if (! all(unique(x$Initiator) %in% partic)) {
        cat("Problem with", x$WarNum[1], "\n")
        print(x$Initiator)
        print(partic)
    }
}

