library(msSurv)
library(dplyr)
library(rlist)

file <- read.csv("C:/takeshi/Self_Study/UW/2022_Capstone/code/data/CareerPath/career_path_DelloiteDigital_UK_msSrv_relative.csv")
df <- file %>% select(id, stop, start.stage, end.stage)


df_edg <- df %>% group_by(start.stage, end.stage) %>% summarize(num_edg=n())
df_edg <- data.frame(df_edg)  
#df_edg <- df_edg[-1, ] #Remove header row

src_node_list <- unique(df_edg$start.stage)
trg_node_list <- unique(df_edg$end.stage[df_edg$end.stage != "0"]) #List all node except for Right-censoring(0)
all_node <- c(as.character(src_node_list), as.character(trg_node_list))
all_node <- unique(all_node)

Edges = list()
for ( src in src_node_list) {
  trg_node <- df_edg$end.stage[df_edg$start.stage == src & df_edg$end.stage != src & df_edg$end.stage != 0]
  trg_node <- as.character(trg_node)
  edg <- list(edges = trg_node)
  src_idx <- as.character(src)
  #Edges <- append(Edges, list(trg_node))
  Edges <- append(Edges, edg)
}

terminal <- list()
for ( trg in trg_node_list) {
  cnt_src <- nrow(df_edg[df_edg$start.stage == trg,])
  if (cnt_src ==0){ #No transition from trg. Trg is the terminal state
    edg <- list(edges = NULL)
    Edges <- append(Edges, edg)
    terminal <- append(terminal, as.character(trg))
  }
}

vec_node <- c(as.character(src_node_list), unlist(terminal))

Edges_in <- list()
for ( i in 1 : length(vec_node))  {
  Edges_in[[i]] <- Edges[i]
}

names(Edges_in) <- vec_node



treeObj <- new("graphNEL", nodes = all_node, edgeL=Edges_in,
               edgemode = "directed")



ex1 <- msSurv(df, treeObj, bs = FALSE)

print(ex1)

#Plot Transition Probabilities
plot(ex1,  plot.type = "transprob")



#State occupation probabilities at a specific time t
SOPt(ex1, t = 12)
SOPt(ex1, t = 24)
SOPt(ex1, t = 36)
SOPt(ex1, t = 48)
SOPt(ex1, t = 60)

#Show state transition probability for one year
pst1 <- Pst(ex1, s = 1, t = 6)
pst2 <- Pst(ex1, s = 6, t = 12)
pst3 <- Pst(ex1, s = 12, t = 18)
pst4 <- Pst(ex1, s = 18, t = 24)
pst5 <- Pst(ex1, s = 24, t = 30)
pst6 <- Pst(ex1, s = 30, t = 36)
pst7 <- Pst(ex1, s = 36, t = 42)
pst8 <- Pst(ex1, s = 42, t = 48)
pst9 <- Pst(ex1, s = 48, t = 54)
pst10 <- Pst(ex1, s = 54, t = 60)


out_dir = "C:/takeshi/Self_Study/UW/2022_Capstone/code/data/TranProb"

write.csv(pst1, file=paste0(out_dir, "/pst1.csv"))
write.csv(pst2, file=paste0(out_dir,"/pst2.csv"))
write.csv(pst3, file=paste0(out_dir,"/pst3.csv"))
write.csv(pst4, file=paste0(out_dir,"/pst4.csv"))
write.csv(pst5, file=paste0(out_dir,"/pst5.csv"))
write.csv(pst6, file=paste0(out_dir,"/pst6.csv"))
write.csv(pst7, file=paste0(out_dir,"/pst7.csv"))
write.csv(pst8, file=paste0(out_dir,"/pst8.csv"))
write.csv(pst9, file=paste0(out_dir,"/pst9.csv"))
write.csv(pst10, file=paste0(out_dir,"/pst10.csv"))

summary(ex1, stateocc=FALSE, trans.pr=TRUE, dist=FALSE, times=c(6,12,18,24,30,36,42,48,54,60))


